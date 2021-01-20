try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from typing import Union
from pydantic import (
    BaseModel,
    root_validator,
    validator,
    conint,
    Extra,
    StrictFloat,
    StrictInt,
)

#  pylint: disable=too-few-public-methods,no-self-argument


class BaseMisfitPreprocessorConfig(BaseModel):
    class Config:
        validate_all = True
        validate_assignment = True
        allow_mutation = False
        arbitrary_types_allowed = True
        extra = Extra.forbid


class BaseFclusterConfig(BaseMisfitPreprocessorConfig):
    """
    The fcluster implementation is backed by scipy and for a
    more detailed description we refer the reader to the
    documentation of scipy.cluster.hierarchy.fcluster`
    (https://docs.scipy.org/doc/scipy/reference/generated
    /scipy.cluster.hierarchy.fcluster.html).
    """

    depth: conint(gt=0) = 2

    @validator("depth", pre=True)
    def constrained_int(cls, depth):
        if isinstance(depth, float):
            raise ValueError("Depth must be int")
        return depth


class FclusterConfig(BaseFclusterConfig):
    __doc__ = BaseFclusterConfig.__doc__
    threshold: Union[StrictInt, StrictFloat] = 1.15
    criterion: Literal[
        "inconsistent", "distance", "maxclust", "monocrit", "maxclust_monocrit"
    ] = "inconsistent"

    @root_validator(pre=True)
    def validate_threshold(cls, values):
        criterion = values.get("criterion")
        threshold = values.get("threshold")
        if criterion in ("maxclust", "maxclust_monocrit") and "threshold" not in values:
            values["threshold"] = 5
        if criterion in ("maxclust", "maxclust_monocrit") and threshold:
            if isinstance(threshold, float):
                raise TypeError(
                    "threshold must be an integer if a max cluster criteria is chosen"
                )
        return values

    @validator("threshold")
    def t_larger_than_zero(cls, threshold):
        if threshold <= 0:
            raise ValueError(f"threshold must be larger than zero, is {threshold}")
        return threshold


class LinkageConfig(BaseMisfitPreprocessorConfig):
    """
    The linkage implementation is backed by scipy and for a
    more detailed description we refer the reader to the
    documentation of scipy.cluster.hierarchy.linkage`
    (https://docs.scipy.org/doc/scipy/reference/generated
    /scipy.cluster.hierarchy.linkage.html).
    """

    method: Literal[
        "single",
        "complete",
        "average",
        "weighted",
        "centroid",
        "ward",
    ] = "average"
    metric: Literal[
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
    ] = "euclidean"


class HierarchicalConfig(BaseMisfitPreprocessorConfig):
    type: Literal["hierarchical"] = "hierarchical"
    linkage: LinkageConfig = LinkageConfig()
    fcluster: FclusterConfig = FclusterConfig()

    def dict(self):
        cluster_args = self.linkage.dict()
        cluster_args.update(self.fcluster.dict())
        return cluster_args


class LimitedHierarchicalConfig(BaseMisfitPreprocessorConfig):
    type: Literal["limited_hierarchical"] = "limited_hierarchical"
    linkage: LinkageConfig = LinkageConfig()
    fcluster: BaseFclusterConfig = BaseFclusterConfig()