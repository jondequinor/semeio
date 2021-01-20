import pydantic
import pytest

from semeio.workflows.misfit_preprocessor import workflow_config, hierarchical_config
from semeio.workflows.misfit_preprocessor.exceptions import ValidationError
from semeio.workflows import misfit_preprocessor
from semeio.workflows.misfit_preprocessor.hierarchical_config import HierarchicalConfig


@pytest.mark.parametrize("workflow", ["spearman_correlation", "auto_scale"])
@pytest.mark.parametrize(
    "threshold",
    [
        (0.001),
        (0.5),
        (0.999),
    ],
)
def test_valid_scaling_threshold(threshold, workflow):
    config_data = {"workflow": {"type": workflow, "pca": {"threshold": threshold}}}

    config = workflow_config.MisfitConfig(**config_data)
    assert config.workflow.pca.threshold == threshold


@pytest.mark.parametrize("workflow", ["spearman_correlation", "auto_scale"])
@pytest.mark.parametrize(
    "threshold, expected_error",
    [
        (-1, "ensure this value is greater than 0"),
        (0, "ensure this value is greater than 0"),
        (10, "ensure this value is less than or equal to 1.0"),
        (1.0001, "ensure this value is less than or equal to 1.0"),
    ],
)
def test_invalid_scaling_threshold(threshold, workflow, expected_error):
    config_data = {"workflow": {"type": workflow, "pca": {"threshold": threshold}}}
    with pytest.raises(pydantic.ValidationError, match=expected_error):
        workflow_config.MisfitConfig(**config_data)


def test_default_scaling_threshold():
    config = workflow_config.MisfitConfig()
    assert config.workflow.pca.threshold == 0.95


@pytest.mark.parametrize("clustering_method", ["auto_scale", "spearman_correlation"])
def test_valid_clustering_method(clustering_method):
    config_data = {"workflow": {"type": clustering_method}}
    config = misfit_preprocessor.config.assemble_config(
        config_data, ("some_observation",)
    )
    assert config.workflow.type == clustering_method


@pytest.mark.parametrize("clustering_method", ["super_clustering", None])
def test_invalid_clustering_method(clustering_method):
    config_data = {"workflow": {"type": clustering_method}}
    with pytest.raises(
        ValidationError, match=f"- Unknown workflow {clustering_method}"
    ):
        misfit_preprocessor.config.assemble_config(config_data, ("some_observation",))


def test_default_clustering_method():
    config = workflow_config.MisfitConfig()
    assert config.workflow.type == "auto_scale"


@pytest.mark.parametrize(
    "threshold, criterion",
    [
        (12, "inconsistent"),
        (12, "distance"),
        (12, "maxclust"),
        (12, "monocrit"),
        (12, "maxclust_monocrit"),
        (1.2, "inconsistent"),
        (1.2, "distance"),
        (1.2, "monocrit"),
    ],
)
def test_valid_spearman_threshold(threshold, criterion):
    config_data = {"fcluster": {"criterion": criterion, "threshold": threshold}}
    hierarchical_config.HierarchicalConfig(**config_data)


@pytest.mark.parametrize(
    "threshold, criterion",
    [
        (None, "inconsistent"),
        (None, "distance"),
        (None, "maxclust"),
        (None, "monocrit"),
        (None, "maxclust_monocrit"),
        (0, "inconsistent"),
        (0, "distance"),
        (0, "maxclust"),
        (0, "monocrit"),
        (0, "maxclust_monocrit"),
        (1.2, "maxclust"),
        (1.2, "maxclust_monocrit"),
    ],
)
def test_invalid_spearman_threshold(threshold, criterion):
    config_data = {"fcluster": {"criterion": criterion, "threshold": threshold}}
    with pytest.raises(pydantic.ValidationError):
        HierarchicalConfig(**config_data)


@pytest.mark.parametrize(
    "criterion, default_threshold",
    [
        ("inconsistent", 1.15),
        ("distance", 1.15),
        ("maxclust", 5),
        ("monocrit", 1.15),
        ("maxclust_monocrit", 5),
    ],
)
def test_default_spearman_threshold(criterion, default_threshold):
    config_data = {"fcluster": {"criterion": criterion}}
    config = hierarchical_config.HierarchicalConfig(**config_data)

    assert config.fcluster.threshold == default_threshold


@pytest.mark.parametrize(
    "depth",
    [1, 2, 10 ** 10],
)
def test_valid_depth(depth):
    config_data = {"fcluster": {"depth": depth}}
    hierarchical_config.HierarchicalConfig(**config_data)


@pytest.mark.parametrize(
    "depth",
    [-10, 0, None, 1.5],
)
def test_invalid_depth(depth):
    config_data = {"fcluster": {"depth": depth}}
    with pytest.raises(pydantic.ValidationError):
        hierarchical_config.HierarchicalConfig(**config_data)


def test_default_fcluster_depth():
    config = hierarchical_config.HierarchicalConfig()
    assert config.fcluster.depth == 2


@pytest.mark.parametrize(
    "method",
    [
        "single",
        "complete",
        "average",
        "weighted",
        "centroid",
        "ward",
    ],
)
def test_valid_linkage_method(method):
    config_data = {"linkage": {"method": method}}
    hierarchical_config.HierarchicalConfig(**config_data)


@pytest.mark.parametrize(
    "method",
    [
        (None, False),
        ("secret", False),
    ],
)
def test_invalid_linkage_method(method):
    config_data = {"linkage": {"method": method}}
    with pytest.raises(pydantic.ValidationError):
        hierarchical_config.HierarchicalConfig(**config_data)


def test_default_linkage_method():
    config_data = {}
    config = hierarchical_config.HierarchicalConfig(**config_data)
    assert config.linkage.method == "average"


@pytest.mark.parametrize(
    "metric",
    [
        "braycurtis",
        "canberra",
        "chebyshev",
        "cityblock",
        "correlation",
        "cosine",
        "dice",
        "euclidean",
        "hamming",
        "jaccard",
        "jensenshannon",
        "kulsinski",
        "mahalanobis",
        "matching",
        "minkowski",
        "rogerstanimoto",
        "russellrao",
        "seuclidean",
        "sokalmichener",
        "sokalsneath",
        "sqeuclidean",
        "yule",
    ],
)
def test_valid_linkage_metric(metric):
    config_data = {"linkage": {"metric": metric}}
    hierarchical_config.HierarchicalConfig(**config_data)


@pytest.mark.parametrize("metric", [None, "secret"])
def test_invalid_linkage_metric(metric):
    config_data = {"linkage": {"metric": metric}}
    with pytest.raises(pydantic.ValidationError):
        hierarchical_config.HierarchicalConfig(**config_data)


def test_default_linkage_metric():
    config_data = {}
    config = hierarchical_config.HierarchicalConfig(**config_data)
    assert "euclidean" == config.linkage.metric


@pytest.mark.parametrize(
    "observation_filter, observation_keys, expected_obs",
    [
        (("my_obs",), ("my_obs", "other_obs"), ("my_obs",)),
        (("my_obs", "obs1"), ("my_obs", "other_obs", "obs1"), ("my_obs", "obs1")),
        (("*",), ("my_obs", "other_obs"), ("my_obs", "other_obs")),
        (
            ("*1", "*2"),
            ("a1", "a2", "a3", "aa1", "aa2", "aa3"),
            ("a1", "a2", "aa1", "aa2"),
        ),
    ],
)
def test_valid_observations(
    observation_filter,
    observation_keys,
    expected_obs,
):
    config_data = {"observations": observation_filter}
    config = misfit_preprocessor.config.assemble_config(config_data, observation_keys)
    assert sorted(config.observations) == sorted(expected_obs)


@pytest.mark.parametrize(
    "observation_filter, observation_keys, expected_obs, expected_error",
    [
        (
            ("secret_obs",),
            ("my_obs", "other_obs"),
            (),
            "Found no match for observation secret_obs",
        ),
        (
            ("*1", "*2", "*5"),
            ("a1", "a2", "a3", "aa1", "aa2", "aa3"),
            ("a1", "a2", "aa1", "aa2"),
            r"Found no match for observation \*5",
        ),
    ],
)
def test_invalid_observations(
    observation_filter,
    observation_keys,
    expected_obs,
    expected_error,
):
    config_data = {"observations": observation_filter}
    with pytest.raises(ValidationError, match=expected_error):
        misfit_preprocessor.config.assemble_config(config_data, observation_keys)


@pytest.mark.parametrize(
    "observation_keys",
    [
        ("my_obs", "other_obs"),
        ("my_obs", "other_obs", "obs1") + tuple(i * "a" for i in range(20)),
        ("my_obs", "other_obs"),
    ],
)
def test_default_observations(observation_keys):
    config_data = {}
    config = misfit_preprocessor.config.assemble_config(config_data, observation_keys)
    assert sorted(config.observations) == sorted(observation_keys)


@pytest.mark.parametrize(
    "key, expected_error",
    [
        ["threshold", "workflow -> clustering -> fcluster -> threshold"],
        ["criterion", "workflow -> clustering -> fcluster -> criterion"],
    ],
)
def test_auto_scale_invalid_fcluster(key, expected_error):
    config_data = {"type": "auto_scale", "clustering": {"fcluster": {key: 0.1}}}
    with pytest.raises(pydantic.ValidationError, match=expected_error):
        workflow_config.MisfitConfig(workflow=config_data)


def test_config_workflow():
    config_data = {
        "observations": ["WWPR"],
        "workflow": {
            "type": "spearman_correlation",
            "clustering": {
                "linkage": {"method": "complete", "metric": "jensenshannon"}
            },
            "pca": {"threshold": 0.98},
        },
    }
    config = workflow_config.MisfitConfig(**config_data)
    assert config.workflow.type == "spearman_correlation"


@pytest.mark.parametrize("workflow", ["spearman_correlation", "auto_scale"])
def test_config_workflow_valid(workflow):
    config_data = {"workflow": {"type": workflow}}
    config = workflow_config.MisfitConfig(**config_data)
    assert config.workflow.type == workflow
