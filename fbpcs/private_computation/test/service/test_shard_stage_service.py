#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import defaultdict
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from fbpcs.data_processing.service.sharding_service import ShardingService
from fbpcs.onedocker_binary_config import OneDockerBinaryConfig
from fbpcs.private_computation.entity.private_computation_instance import (
    PrivateComputationGameType,
    PrivateComputationInstance,
    PrivateComputationRole,
)
from fbpcs.private_computation.entity.private_computation_instance import (
    PrivateComputationInstanceStatus,
)
from fbpcs.private_computation.service.constants import (
    NUM_NEW_SHARDS_PER_FILE,
)
from fbpcs.private_computation.service.shard_stage_service import (
    ShardStageService,
)


class TestShardStageService(IsolatedAsyncioTestCase):
    @patch("fbpcp.service.onedocker.OneDockerService")
    def setUp(self, onedocker_service) -> None:
        self.onedocker_service = onedocker_service
        self.test_num_containers = 2

        self.onedocker_binary_config_map = defaultdict(
            lambda: OneDockerBinaryConfig(
                tmp_directory="/test_tmp_directory/", binary_version="latest"
            )
        )
        self.stage_svc = ShardStageService(
            self.onedocker_service, self.onedocker_binary_config_map
        )

    async def test_reshard_data(self) -> None:
        private_computation_instance = self.create_sample_instance()

        with patch.object(
            ShardingService,
            "start_containers",
        ) as mock_shard:
            # call re-sharding
            await self.stage_svc.run_async(private_computation_instance)
            mock_shard.assert_called()

    def create_sample_instance(self) -> PrivateComputationInstance:
        return PrivateComputationInstance(
            instance_id="test_instance_123",
            role=PrivateComputationRole.PARTNER,
            instances=[],
            status=PrivateComputationInstanceStatus.ID_MATCHING_COMPLETED,
            status_update_ts=1600000000,
            num_pid_containers=self.test_num_containers,
            num_mpc_containers=self.test_num_containers,
            num_files_per_mpc_container=NUM_NEW_SHARDS_PER_FILE,
            game_type=PrivateComputationGameType.LIFT,
            input_path="456",
            output_dir="789",
        )
