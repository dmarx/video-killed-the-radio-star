from vktrs.project_harness import Project, Workspace
from omegaconf import OmegaConf, DictConfig
from pathlib import Path
import pytest
from loguru import logger


def test_project_vanilla_init():
    p = Project()
    assert len(p.name.strip()) > 0
    assert p.name in str(p.root)
    assert p.root.exists()
    assert p.cfg_fpath.exists()
    assert isinstance(p.cfg, DictConfig)

def test_project_load():
    p = Project(foo='bar')
    p2 = Project(name=p.name)
    assert p2.cfg.foo == 'bar'

def test_project_checkpoint_and_refresh():
    p = Project()
    assert 'foo' not in p.cfg
    p.cfg['foo'] = 'bar'
    
    # initializes using config on disk, which foo has not yet been written to
    p2 = Project(name=p.name)
    assert 'foo' not in p2.cfg
    p.checkpoint()
    # after checkpointing, it loads
    p3 = Project(name=p.name)
    assert p3.cfg.foo == 'bar'

    # still not attached to p2 since it doesn't know to update
    assert 'foo' not in p2.cfg
    # if we trigger a refresh, we're all up to date
    p2.reload()
    assert p2.cfg.foo == 'bar'

#################################################

def test_workspace_vanilla_init():
    w = Workspace()
    assert w.name is None
    assert w.root.exists()
    assert w.cfg_fpath.exists()
    assert isinstance(w.cfg, DictConfig)
    #################
    assert isinstance(w.active_project, Project)

def test_workspace_init_named_project():
    projname = 'testproj'
    w = Workspace(active_project_name=projname)
    logger.debug(w.cfg)
    assert w.active_project.name == projname
