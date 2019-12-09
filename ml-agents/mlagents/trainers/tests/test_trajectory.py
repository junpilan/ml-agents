import numpy as np
import pytest

from mlagents.trainers.trajectory import (
    AgentExperience,
    Trajectory,
    split_obs,
    trajectory_to_agentbuffer,
)

VEC_OBS_SIZE = 6
ACTION_SIZE = 4


def make_fake_trajectory(length: int, max_step_complete: bool = False) -> Trajectory:
    """
    Makes a fake trajectory of length length. If max_step_complete,
    the trajectory is terminated by a max step rather than a done.
    """
    steps_list = []
    for i in range(length - 1):
        obs = [np.ones((84, 84, 3)), np.ones(VEC_OBS_SIZE)]
        reward = 1.0
        done = False
        action = np.zeros(ACTION_SIZE)
        action_probs = np.ones(ACTION_SIZE)
        action_pre = np.zeros(ACTION_SIZE)
        action_mask = np.ones(ACTION_SIZE)
        prev_action = np.ones(ACTION_SIZE)
        max_step = False
        memory = np.ones(10)
        agent_id = "test_agent"
        experience = AgentExperience(
            obs=obs,
            reward=reward,
            done=done,
            action=action,
            action_probs=action_probs,
            action_pre=action_pre,
            action_mask=action_mask,
            prev_action=prev_action,
            max_step=max_step,
            memory=memory,
            agent_id=agent_id,
        )
        steps_list.append(experience)
    last_experience = AgentExperience(
        obs=obs,
        reward=reward,
        done=not max_step_complete,
        action=action,
        action_probs=action_probs,
        action_pre=action_pre,
        action_mask=action_mask,
        prev_action=prev_action,
        max_step=max_step_complete,
        memory=memory,
        agent_id=agent_id,
    )
    steps_list.append(last_experience)
    bootstrap_step = experience
    return Trajectory(steps=steps_list, bootstrap_step=bootstrap_step)


@pytest.mark.parametrize("num_visual_obs", [0, 1, 2])
@pytest.mark.parametrize("num_vec_obs", [0, 1])
def test_split_obs(num_visual_obs, num_vec_obs):
    obs = []
    for i in range(num_visual_obs):
        obs.append(np.ones((84, 84, 3), dtype=np.float32))
    for i in range(num_vec_obs):
        obs.append(np.ones(VEC_OBS_SIZE))
    split_observations = split_obs(obs)

    if num_vec_obs == 1:
        assert len(split_observations.vector_observations) == VEC_OBS_SIZE
    else:
        assert len(split_observations.vector_observations) == 0

    # Assert the number of vector observations.
    assert len(split_observations.visual_observations) == num_visual_obs


def test_trajectory_to_agentbuffer():
    length = 15
    wanted_keys = [
        "next_visual_obs0",
        "visual_obs0",
        "vector_obs",
        "next_vector_in",
        "memory",
        "masks",
        "done",
        "actions_pre",
        "actions",
        "action_probs",
        "action_mask",
        "prev_action",
        "environment_rewards",
    ]
    wanted_keys = set(wanted_keys)
    trajectory = make_fake_trajectory(length=length)
    agentbuffer = trajectory_to_agentbuffer(trajectory)
    seen_keys = set()
    for key, field in agentbuffer.items():
        assert len(field) == length
        seen_keys.add(key)

    assert seen_keys == wanted_keys
