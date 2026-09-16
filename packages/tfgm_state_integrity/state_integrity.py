#!/usr/bin/env python3
"""SI-F0 State Integrity Foundation.

Model-neutral state classification and transition authorization primitives.

This module deliberately keeps evidence, authority, temporal validity,
applicability, integrity, and status separate. It does not infer authority
from provenance grade and does not treat model assertions as execution
evidence.
"""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
AUTHENTIC="AUTHENTIC"; CURRENT="CURRENT"; SUPERSEDED="SUPERSEDED"; AUTHORITATIVE="AUTHORITATIVE"; ACTIONABLE="ACTIONABLE"; NOT_ACTIONABLE="NOT_ACTIONABLE"; CONTEXT_DEPENDENT="CONTEXT_DEPENDENT"
CLAIMED="CLAIMED"; EXECUTED="EXECUTED"; OBSERVED="OBSERVED"; VERIFIED="VERIFIED"; NOT_COMPLETED="NOT_COMPLETED"
REPLAN="REPLAN"; REQUEST_EVIDENCE="REQUEST_EVIDENCE"; ESCALATE="ESCALATE"; BLOCK="BLOCK"; CONTINUE="CONTINUE"
def _canonical(value:object)->str:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def digest(value:object)->str:return "sha256:"+hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()
@dataclass(frozen=True)
class StateItem:
    state_id:str; subject:str; value:object; status:str; provenance:str; authority:str; scope:str; effective_from:str; effective_until:str|None; supersedes:str|None; source_warrant:str; source_revision:str; integrity_digest:str
    @staticmethod
    def mint(*,state_id:str,subject:str,value:object,status:str,provenance:str,authority:str,scope:str,effective_from:str,effective_until:str|None=None,supersedes:str|None=None,source_warrant:str="",source_revision:str="")->"StateItem":
        datetime.fromisoformat(effective_from.replace("Z","+00:00"))
        if effective_until is not None:
            start=datetime.fromisoformat(effective_from.replace("Z","+00:00"));end=datetime.fromisoformat(effective_until.replace("Z","+00:00"))
            if end<start:raise ValueError("INVALID_EFFECTIVE_RANGE")
        body={"state_id":state_id,"subject":subject,"value":value,"status":status,"provenance":provenance,"authority":authority,"scope":scope,"effective_from":effective_from,"effective_until":effective_until,"supersedes":supersedes,"source_warrant":source_warrant,"source_revision":source_revision}
        return StateItem(**body,integrity_digest=digest(body))
    def verify_integrity(self)->bool:
        body={"state_id":self.state_id,"subject":self.subject,"value":self.value,"status":self.status,"provenance":self.provenance,"authority":self.authority,"scope":self.scope,"effective_from":self.effective_from,"effective_until":self.effective_until,"supersedes":self.supersedes,"source_warrant":self.source_warrant,"source_revision":self.source_revision}
        return self.integrity_digest==digest(body)
@dataclass(frozen=True)
class AuthorityRule:
    subject:str; scope:str; authority:str
    def matches(self,state:StateItem,subject:str,scope:str)->bool:
        return state.subject==subject and (self.scope==scope or self.scope=="*") and (state.scope==scope or state.scope=="*") and self.authority==state.authority
@dataclass(frozen=True)
class StateClassification:
    state_id:str; authentic:bool; current:bool; superseded:bool; authoritative:bool|None; actionable:bool; reasons:tuple[str,...]
def _in_window(state:StateItem,at:str)->bool:
    now=datetime.fromisoformat(at.replace("Z","+00:00"));start=datetime.fromisoformat(state.effective_from.replace("Z","+00:00"))
    if now<start:return False
    if state.effective_until is None:return True
    end=datetime.fromisoformat(state.effective_until.replace("Z","+00:00"));return now<=end
def classify_state(state:StateItem,*,at:str,subject:str,scope:str,superseded_ids:Iterable[str]=(),authority_rules:Iterable[AuthorityRule]=(),warranted_state_ids:Iterable[str]=())->StateClassification:
    reasons=[];authentic=state.verify_integrity()
    if not authentic:reasons.append("INTEGRITY_FAILURE")
    superseded=state.state_id in set(superseded_ids);current=_in_window(state,at) and not superseded
    if not current:reasons.append("NOT_CURRENT")
    matches=[r for r in authority_rules if r.matches(state,subject,scope)]
    if not matches:authoritative=None;reasons.append("AUTHORITY_CONTEXT_DEPENDENT")
    else:authoritative=True
    warranted=state.state_id in set(warranted_state_ids);actionable=bool(authentic and current and authoritative is True and warranted)
    if not warranted:reasons.append("WARRANT_NOT_ESTABLISHED")
    if not actionable:reasons.append("NOT_ACTIONABLE")
    return StateClassification(state.state_id,authentic,current,superseded,authoritative,actionable,tuple(sorted(set(reasons))))
@dataclass(frozen=True)
class OutcomeClaim:
    task_id:str; statement:str; status:str; execution_evidence_ids:tuple[str,...]=(); observed_evidence_ids:tuple[str,...]=(); verified_evidence_ids:tuple[str,...]=(); observed_at:str|None=None
    @property
    def completion_licensed(self)->bool:return bool(self.execution_evidence_ids and self.verified_evidence_ids)
def adjudicate_outcome(claim:OutcomeClaim)->str:
    if claim.status!=CLAIMED:raise ValueError("OUTCOME_CLAIM_MUST_START_AS_CLAIMED")
    return "COMPLETED" if claim.completion_licensed else NOT_COMPLETED
@dataclass(frozen=True)
class ProgressAttempt:
    attempt_id:str; failure_class:str|None; state_digest:str; meaningful_delta:bool
def continuation_decision(attempts:Iterable[ProgressAttempt])->str:
    ordered=tuple(attempts)
    if len(ordered)<2:return CONTINUE
    latest=ordered[-1];prior=ordered[-2];same_failure=latest.failure_class is not None and latest.failure_class==prior.failure_class;no_delta=latest.state_digest==prior.state_digest and not latest.meaningful_delta
    if same_failure and no_delta:return REQUEST_EVIDENCE
    return CONTINUE
__all__=[name for name in globals() if not name.startswith("_")]
