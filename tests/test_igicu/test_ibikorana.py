"""Tests for IGICU DevOps (ibikorana)."""

from __future__ import annotations

import pytest

from igicu.ibikorana import (
    Pipeline, CICDManager, EnvironmentManager,
    ReleaseManager, ConfigManager, IaCManager,
    DisasterRecovery, DevOpsPlatform,
)


class TestPipeline:
    def test_add_stage(self):
        p = Pipeline("build")
        stage_id = p.add_stage("compile", ["i build"], ["fetch-deps"])
        assert stage_id is not None

    def test_run(self):
        p = Pipeline("ci")
        p.add_stage("lint", ["i lint"])
        p.add_stage("test", ["i test"], depends_on=["lint"])
        results = p.run()
        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)

    def test_set_env(self):
        p = Pipeline("deploy")
        p.set_env("DEPLOY_ENV", "production")
        status = p.get_status()
        assert status["env_count"] == 1


class TestCICDManager:
    def test_create_pipeline(self):
        cm = CICDManager()
        p = cm.create_pipeline("main")
        assert p is not None

    def test_get_pipeline(self):
        cm = CICDManager()
        cm.create_pipeline("test-pipe")
        p = cm.get_pipeline("test-pipe")
        assert p is not None

    def test_list_pipelines(self):
        cm = CICDManager()
        cm.create_pipeline("p1")
        cm.create_pipeline("p2")
        pipelines = cm.list_pipelines()
        assert len(pipelines) >= 2

    def test_run_pipeline(self):
        cm = CICDManager()
        p = cm.create_pipeline("ci-cd")
        p.add_stage("build", ["i build"])
        results = cm.run_pipeline("ci-cd")
        assert len(results) == 1

    def test_get_run_history(self):
        cm = CICDManager()
        p = cm.create_pipeline("history")
        p.add_stage("test", ["i test"])
        cm.run_pipeline("history")
        history = cm.get_run_history("history")
        assert len(history) >= 1


class TestEnvironmentManager:
    def test_create(self):
        em = EnvironmentManager()
        env_id = em.create("staging", "staging", {"API_KEY": "test"})
        assert env_id is not None

    def test_get(self):
        em = EnvironmentManager()
        em.create("prod", "production")
        env = em.get("prod")
        assert env is not None
        assert env["type"] == "production"

    def test_list(self):
        em = EnvironmentManager()
        em.create("dev", "development")
        em.create("prod", "production")
        envs = em.list()
        assert len(envs) == 2

    def test_set_and_get_variable(self):
        em = EnvironmentManager()
        em.create("test", "test")
        assert em.set_variable("test", "DB_URL", "postgres://localhost") is True
        assert em.get_variable("test", "DB_URL") == "postgres://localhost"

    def test_delete(self):
        em = EnvironmentManager()
        em.create("temp", "temp")
        assert em.delete("temp") is True

    def test_promote(self):
        em = EnvironmentManager()
        em.create("dev", "development", {"KEY": "dev-value"})
        em.create("prod", "production")
        assert em.promote("dev", "prod") is True


class TestReleaseManager:
    def test_create(self):
        rm = ReleaseManager()
        rel_id = rm.create("v1.0", "1.0.0", {"binary": "app.bin"})
        assert rel_id is not None

    def test_publish(self):
        rm = ReleaseManager()
        rel_id = rm.create("v1", "1.0")
        assert rm.publish(rel_id) is True

    def test_rollback(self):
        rm = ReleaseManager()
        rel_id = rm.create("v1", "1.0")
        rm.publish(rel_id)
        result = rm.rollback(rel_id)
        assert result is not None

    def test_list(self):
        rm = ReleaseManager()
        rm.create("v1", "1.0")
        rm.create("v2", "2.0")
        releases = rm.list()
        assert len(releases) == 2


class TestIaCManager:
    def test_define_stack(self):
        iac = IaCManager()
        stack_id = iac.define_stack("infra", [{"type": "vpc", "name": "main"}])
        assert stack_id is not None

    def test_deploy_stack(self):
        iac = IaCManager()
        iac.define_stack("web", [{"type": "server"}])
        result = iac.deploy_stack("web")
        assert result["status"] == "deployed"

    def test_destroy_stack(self):
        iac = IaCManager()
        iac.define_stack("temp", [])
        result = iac.destroy_stack("temp")
        assert result["status"] == "destroyed"


class TestDisasterRecovery:
    def test_create_backup(self):
        dr = DisasterRecovery()
        backup_id = dr.create_backup("daily", "db1")
        assert backup_id is not None

    def test_restore(self):
        dr = DisasterRecovery()
        backup_id = dr.create_backup("weekly", "db1")
        result = dr.restore(backup_id)
        assert result["status"] == "restored"

    def test_list_backups(self):
        dr = DisasterRecovery()
        dr.create_backup("b1", "db1")
        dr.create_backup("b2", "db2")
        backups = dr.list_backups()
        assert len(backups) == 2

    def test_create_plan(self):
        dr = DisasterRecovery()
        plan_id = dr.create_plan("recovery", [{"name": "restore_db"}])
        assert plan_id is not None

    def test_execute_plan(self):
        dr = DisasterRecovery()
        plan_id = dr.create_plan("dr-plan", [{"name": "step1"}, {"name": "step2"}])
        result = dr.execute_plan(plan_id)
        assert result["status"] == "completed"


class TestDevOpsPlatform:
    def test_full_platform(self):
        devops = DevOpsPlatform()
        assert devops.ci_cd is not None
        assert devops.environments is not None
        assert devops.releases is not None
        assert devops.config is not None
        assert devops.iac is not None
        assert devops.disaster_recovery is not None
