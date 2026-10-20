"""Testes de continuidade real em worktrees temporárias; não testa a Trama."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/tarefa.py"
TEMPLATE = Path(__file__).resolve().parents[1] / "templates/checkpoint.json"


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@local.invalid")
        (self.root / ".gitignore").write_text("/agentes/\n")
        (self.root / "program.txt").write_text("base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")

    def git(self, *args, root=None):
        return subprocess.run(["git", "-C", str(root or self.root), *args],
                              capture_output=True, text=True, check=True).stdout.strip()

    def command(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.root), *args],
                           capture_output=True, text=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("error", json.loads(p.stderr))
        return p

    def start(self, task="feature", slot="a001", ok=True):
        return self.command("iniciar", "--slot", slot, "--tarefa", task,
                            "--executor", "alpha", "--issue",
                            "https://github.com/example/repo/issues/1", ok=ok)

    def checkpoint(self, path, owner="alpha", generation="1", ok=True):
        return self.command("checkpoint", "--slot", "a001", "--executor", owner,
                            "--geracao", generation, "--arquivo", str(path), ok=ok)

    def transfer(self, ok=True, confirmation=True):
        args = ["transferir", "--slot", "a001", "--executor", "alpha", "--geracao", "1",
                "--para", "beta", "--motivo", "Sessão encerrada; exclusividade conferida"]
        if confirmation:
            args.append("--confirmar-exclusividade")
        return self.command(*args, ok=ok)

    def test_handoff_preserves_dirty_and_untracked_work_and_checkpoint(self):
        self.start()
        wt = self.root / "agentes/a001/worktree"
        (wt / "program.txt").write_text("trabalho parcial\n")
        (wt / "untracked.txt").write_text("não perder\n")
        payload = json.loads(TEMPLATE.read_text())
        payload["partial"] = ["Implementação parcial no program.txt"]
        path = self.root / "agentes/a001/memory/progresso.json"
        path.write_text(json.dumps(payload))
        self.checkpoint(path)
        self.transfer()
        state = json.loads(self.command("retomar", "--slot", "a001").stdout)
        self.assertEqual(state["state"]["generation"], 2)
        self.assertEqual(state["state"]["executor"], "beta")
        self.assertEqual(state["state"]["checkpoint"]["payload"], payload)
        self.assertEqual((wt / "program.txt").read_text(), "trabalho parcial\n")
        self.assertEqual((wt / "untracked.txt").read_text(), "não perder\n")
        self.assertIn("untracked.txt", state["current"]["git_status"])
        self.assertEqual((self.root / "program.txt").read_text(), "base\n")
        self.assertEqual(self.git("branch", "--show-current", root=wt), "task/feature")
        self.checkpoint(path, ok=False)
        self.checkpoint(path, "beta", "2")
        events = self.command("eventos", "--slot", "a001").stdout.splitlines()
        self.assertEqual([json.loads(e)["event"] for e in events],
                         ["START", "CHECKPOINT", "TRANSFER", "CHECKPOINT"])

    def test_interrupted_owner_not_needed_and_fresh_git_observed(self):
        self.start()
        self.transfer()
        wt = self.root / "agentes/a001/worktree"
        (wt / "later.txt").write_text("after checkpoint")
        state = json.loads(self.command("retomar", "--slot", "a001").stdout)
        self.assertIsNone(state["state"]["checkpoint"])
        self.assertIn("later.txt", state["current"]["git_status"])

    def test_conflicting_slots_and_task_id_are_rejected(self):
        self.start()
        self.start(slot="a002", ok=False)
        self.start(task="other", ok=False)
        self.assertFalse((self.root / "agentes/a002").exists())

    def test_transfer_requires_exclusivity_and_matching_generation(self):
        self.start()
        self.transfer(ok=False, confirmation=False)
        self.transfer()
        self.transfer(ok=False)
        state = json.loads(self.command("observar", "--slot", "a001").stdout)
        self.assertEqual(state["state"]["generation"], 2)

    def test_malformed_checkpoint_leaves_last_revision_intact(self):
        self.start()
        path = self.root / "bad.json"
        path.write_text('{"schema":"pinker.checkpoint/1","schema":"duplicated"}')
        self.checkpoint(path, ok=False)
        state = json.loads(self.command("retomar", "--slot", "a001").stdout)
        self.assertEqual(state["state"]["sequence"], 1)

    def test_corrupt_accepted_revision_and_wrong_branch_fail_closed(self):
        self.start()
        wt = self.root / "agentes/a001/worktree"
        self.git("checkout", "-b", "foreign", root=wt)
        self.command("retomar", "--slot", "a001", ok=False)
        self.git("checkout", "task/feature", root=wt)
        state = self.root / "agentes/a001/estado/00000001.json"
        state.write_text("{")
        self.command("retomar", "--slot", "a001", ok=False)

    def test_symbolic_slot_rejected_without_touching_target(self):
        self.start()
        (self.root / "agentes/a002").symlink_to(self.root / "agentes/a001", target_is_directory=True)
        self.command("retomar", "--slot", "a002", ok=False)
        self.assertTrue((self.root / "agentes/a001/estado/00000001.json").exists())

    def test_failed_publish_and_orphan_temporary_preserve_previous_state(self):
        self.start()
        slot = self.root / "agentes/a001"
        spec = importlib.util.spec_from_file_location("tasks", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state = module.history(slot)[-1]
        with patch.object(module.os, "link", side_effect=OSError("simulated publication failure")):
            with self.assertRaises(OSError):
                module.write_revision(slot, state, "CHECKPOINT")
        (slot / "estado/.pending-interrupted").write_text("{partial")
        result = json.loads(self.command("retomar", "--slot", "a001").stdout)
        self.assertEqual(result["state"]["sequence"], 1)


if __name__ == "__main__":
    unittest.main()
