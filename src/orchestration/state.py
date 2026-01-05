from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class RefactoringState:
    """État partagé entre tous les agents"""
    
    # Configuration
    target_dir: str
    max_iterations: int = 10
    
    # Progression
    current_iteration: int = 0
    current_agent: Optional[str] = None
    
    # Données des agents
    files_to_process: List[str] = field(default_factory=list)
    audit_report: Optional[Dict] = None
    fixed_code: Optional[Dict] = None
    test_results: Optional[Dict] = None
    
    # Métriques
    pylint_score_initial: float = 0.0
    pylint_score_current: float = 0.0
    
    # Contrôle de flux
    tests_passed: bool = False
    agent_status: AgentStatus = AgentStatus.PENDING
    error_message: Optional[str] = None
    
    def should_continue(self) -> bool:
        """Détermine si la boucle doit continuer"""
        if self.tests_passed:
            return False
        if self.current_iteration >= self.max_iterations:
            return False
        if self.agent_status == AgentStatus.FAILED:
            return False
        return True
    
    def increment_iteration(self):
        """Incrémente le compteur d'itération"""
        self.current_iteration += 1