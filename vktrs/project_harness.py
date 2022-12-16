"""
Let's pull out some pieces of this to generalize it beyond this specific notebook a bit more.
Also... let's move most of the remainint logic out of the notebook. cause... ugh.

Anyway, idea with this module is to provide a generic, opinionated project layout to facilitate
- designing notebooks with shared tooling and features, specifically robust resume
- reusing models
"""

from collections import defaultdict
from omegaconf import OmegaConf, DictConfig
from pathlib import Path
import time


class Project:
    def __init__(self, name, parent, config_name='config.yaml'):
        if not name:
            self.name = self.generate_new_project_name
        self.name = name
        if not isinstance(parent, Path):
            parent = Path(parent)
        self.parent
        self.config_name = config_name
        
        # @property attributes constructed from attributes above
        self.root.mkdir(exist_ok=True, parents=True)
        if self.cfg_fpath.exists():
            self.load()
        else:
            self.cfg = self.to_cfg()
            self.checkpoint()

    @property
    def root(self):
        return self.parent / self.name

    @property
    def cfg_fpath(self):
        return self.root / self.config_name

    def generate_new_project_name(self):
        return str(time.time())
    
    def to_cfg():
        _d = {
            'name':self.name,
            'parent':str(self.parent),
            'config_name':str(self.root),
        }
        return OmegaConf.create(_d)
    
    def load(self):
        with self.cfg_fpath.open() as f:
            self.cfg = OmegaConf.load(f)
    
    def checkpoint(self):
        # do something special if already exists to permit rollback? maybe track file in its own little git?
        with self.cfg_fpath.open('w') as f:
            OmegaConf.save(config=self.cfg, f=f)


class ProjectVktrs:
    def __init__(self, name, parent, config_name='storyboard.yaml'):
        super().__init__(name, parent, config_name)



projects_by_type = defaultdict(Project)
projects_by_type['vktrs'] = ProjectVktrs


class Workspace:
    def __init__(
        self,
        cfg_path='config.yaml',
        active_project_name='', # project name 
        project_root='', # where to find the project
        gdrive_mounted='', # motivation here is for use with colab
        model_dir='', # want to make it possible for users to share models across process. save on setup time and storage space.
        #output_dir'', # ok.. maybe this one should be in the project setup and not the workspace. more portable projects this way I guess?
        # nah, output dir should be a project config
        project_type=None
        **kwargs
    ):
        """
        Create a new workspace
        """
        self.gdrive_mounted = gdrive_mounted
        self.model_dir = model_dir

        if Path(cfg_path).exists():
            self.load_workspace(cfg_path)
            return self

        self.cfg_path = cfg_path
        if not project_root:
            project_root = '.'
        self.project_root = Path(project_root)
        if not active_project_name:
            #self.active_project = self.new_project()
            active_project_name = self.generate_new_project_name()
        ProjectFactory = projects_by_type[project_type]
        self.active_project = ProjectFactory(active_project_name, project_root)
        self.addl_args = kwargs
        

    def load_workspace(self, cfg_path=None):
        if cfg_path is None:
            cfg_path = self.cfg_path
        with Path(cfg_path).open() as f:
            cfg = OmegaConf.load(cfg)
            return self.from_config(cfg)

    @staticmethod
    def from_config(cfg:DictConfig):
        raise NotImplementedError

    def to_cfg(self) -> DictConfig:
        _d = {
            'active_project':self.active_project.name,
            'project_root':self.project_root,
            'gdrive_mounted':self.gdrive_mounted,
            'model_dir':self.model_dir,
            'output_dir':self.output_dir,
            #'output_dir':'${active_project}/frames', # sure why not
            ########################################
            #'use_stability_api':use_stability_api,
        }
        _d.update(self.addl_attrs)
        return OmegaConf.create(_d)

    def save(self):
        cfg = self.to_cfg()
        with open(self.cfg_path,'w') as fp:
            OmegaConf.save(config=cfg, f=fp.name)
            
