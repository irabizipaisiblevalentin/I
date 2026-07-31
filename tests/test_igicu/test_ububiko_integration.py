"""Tests for IGICU Database Integration (Ububiko)."""

from __future__ import annotations

import pytest

from igicu.ububiko_integration import (
    UbubikoIntegration, DatabaseDeployment, ReplicaSet,
    ShardConfig, BackupManager, MultiRegionConfig,
)


class TestDatabaseDeployment:
    def test_health(self):
        db = DatabaseDeployment("main", "postgresql", "15.0")
        db.status = "running"
        health = db.health()
        assert health["status"] == "running"
        assert health["engine"] == "postgresql"


class TestReplicaSet:
    def test_health(self):
        rs = ReplicaSet("rs1", "primary-1", ["replica-1", "replica-2"])
        health = rs.health()
        assert health["name"] == "rs1"
        assert health["replicas"] == 2


class TestShardConfig:
    def test_write_and_read(self):
        sc = ShardConfig("users", "user_id", 4)
        sc.write("user:1", {"name": "Alice"})
        data = sc.read("user:1")
        assert data is not None
        assert data["name"] == "Alice"

    def test_shard_distribution(self):
        sc = ShardConfig("orders", "order_id", 3)
        for i in range(10):
            sc.write(f"order:{i}", {"id": i})
        dist = sc.get_shard_distribution()
        assert sum(dist.values()) == 10

    def test_get_shard(self):
        sc = ShardConfig("test", "key", 4)
        shard = sc.get_shard("some-key")
        assert 0 <= shard < 4


class TestBackupManager:
    def test_create(self):
        bm = BackupManager()
        backup_id = bm.create("db1", "full")
        assert backup_id is not None

    def test_restore(self):
        bm = BackupManager()
        backup_id = bm.create("db1")
        result = bm.restore(backup_id, "db2")
        assert result["status"] == "restored"

    def test_list(self):
        bm = BackupManager()
        bm.create("db1")
        bm.create("db1")
        backups = bm.list("db1")
        assert len(backups) == 2


class TestMultiRegionConfig:
    def test_add_region(self):
        mrc = MultiRegionConfig()
        mrc.add_region("us-east", "db.us-east.internal", "read_replica")
        regions = mrc.list_regions()
        assert len(regions) == 1

    def test_promote(self):
        mrc = MultiRegionConfig()
        mrc.add_region("primary", "p.internal", "primary")
        mrc.add_region("dr", "dr.internal", "read_replica")
        assert mrc.promote("dr") is True

    def test_failover(self):
        mrc = MultiRegionConfig()
        mrc.add_region("primary", "p.internal", "primary")
        mrc.add_region("backup", "b.internal", "read_replica")
        new_primary = mrc.failover("primary")
        assert new_primary == "backup"


class TestUbubikoIntegration:
    def test_deploy_database(self):
        integration = UbubikoIntegration()
        db = integration.deploy_database("analytics", "postgresql", region="eu-west")
        assert db.name == "analytics"
        assert db.region == "eu-west"

    def test_list_databases(self):
        integration = UbubikoIntegration()
        integration.deploy_database("db1")
        integration.deploy_database("db2")
        dbs = integration.list_databases()
        assert len(dbs) >= 2

    def test_create_replica_set(self):
        integration = UbubikoIntegration()
        rs = integration.create_replica_set("prod", "primary-1", ["r1", "r2"])
        assert rs.name == "prod"

    def test_create_shard(self):
        integration = UbubikoIntegration()
        sc = integration.create_shard("logs", "timestamp", 6)
        assert sc.shards == 6
