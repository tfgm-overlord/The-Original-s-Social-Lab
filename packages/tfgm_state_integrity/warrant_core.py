#!/usr/bin/env python3
"""Public mirror of TFGM Warrant v0.1 core.

Source: private TFGM repository, warrant/warrant_core.py.
This mirror preserves the model-agnostic evidence/provenance adjudication boundary.
"""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
from datetime import date
from typing import Iterable,Mapping
UNAVAILABLE="UNAVAILABLE"; UNKNOWN="UNKNOWN"; ASSERTED="ASSERTED"; INFERRED="INFERRED"; RECOVERED="RECOVERED"; VERIFIED="VERIFIED"; OBSERVED="OBSERVED"
GRADE:Mapping[str,int]={UNAVAILABLE:0,UNKNOWN:0,ASSERTED:1,INFERRED:2,RECOVERED:3,VERIFIED:4,OBSERVED:5}
PROVENANCE_BY_KIND:Mapping[str,str]={"PROCESS_EXIT":OBSERVED,"STREAM_DIGEST":OBSERVED,"FILE_DIGEST":OBSERVED,"VCS_REF":OBSERVED,"COVERAGE_SCOPE":OBSERVED,"CHECK_RUN":VERIFIED,"LEDGER_HANDLE":RECOVERED,"HUMAN_ATTESTATION":RECOVERED,"INFERENCE":INFERRED,"EXECUTOR_ASSERTION":ASSERTED,"UNAVAILABLE_NOTICE":UNAVAILABLE}
EVIDENCE_KINDS=tuple(sorted(PROVENANCE_BY_KIND))
MISSING_EVIDENCE="MISSING_EVIDENCE"; GRADE_SHORTFALL="GRADE_SHORTFALL"; WRONG_KIND="WRONG_KIND"; UNDELIVERED="UNDELIVERED"; TEMPORALLY_INADMISSIBLE="TEMPORALLY_INADMISSIBLE"; ASSERTION_ONLY="ASSERTION_ONLY"; NEGATIVE_WITHOUT_COVERAGE="NEGATIVE_WITHOUT_COVERAGE"; SUPERSEDED_UNRESOLVED="SUPERSEDED_UNRESOLVED"; KIND_PROVENANCE_MISMATCH="KIND_PROVENANCE_MISMATCH"; EVIDENCE_UNAVAILABLE="EVIDENCE_UNAVAILABLE"; TASK_MISMATCH="TASK_MISMATCH"; PREDICATE_UNSATISFIED="PREDICATE_UNSATISFIED"
REASON_CODES=(MISSING_EVIDENCE,GRADE_SHORTFALL,WRONG_KIND,UNDELIVERED,TEMPORALLY_INADMISSIBLE,ASSERTION_ONLY,NEGATIVE_WITHOUT_COVERAGE,SUPERSEDED_UNRESOLVED,KIND_PROVENANCE_MISMATCH,EVIDENCE_UNAVAILABLE,TASK_MISMATCH,PREDICATE_UNSATISFIED)
DONE="DONE"; NOT_DONE="NOT_DONE"; BLOCKED="BLOCKED"
PREDICATES=("ALL_OF","ANY_OF","EXIT_ZERO","NONEMPTY_STREAM","DIGEST_MATCHES","REF_ADVANCED","COVERS","NONE_FAILED")
class ContractError(ValueError): pass
def _canonical(payload:object)->str:return json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def digest(payload:object)->str:return hashlib.sha256(_canonical(payload).encode()).hexdigest()
@dataclass(frozen=True)
class EvidenceRecord:
    task_id:str; claim_ref:str; kind:str; provenance:str; observed_at:str; payload_digest:str; attributes:tuple[tuple[str,str],...]=(); ledger_handle:str|None=None; supersedes:str|None=None; record_id:str=""
    def attr(self,key:str)->str|None:
        for k,v in self.attributes:
            if k==key:return v
        return None
def make_record(*,task_id:str,claim_ref:str,kind:str,observed_at:str,payload:object,attributes:Mapping[str,str]|None=None,ledger_handle:str|None=None,supersedes:str|None=None,provenance:str|None=None)->EvidenceRecord:
    if kind not in PROVENANCE_BY_KIND:raise ValueError(f"Unknown evidence kind: {kind}")
    attrs=tuple(sorted((str(k),str(v)) for k,v in (attributes or {}).items())); pd=digest(payload); resolved=PROVENANCE_BY_KIND[kind] if provenance is None else provenance
    identity={"task_id":task_id,"claim_ref":claim_ref,"kind":kind,"provenance":resolved,"observed_at":observed_at,"payload_digest":pd,"attributes":[list(a) for a in attrs],"ledger_handle":ledger_handle,"supersedes":supersedes}
    return EvidenceRecord(task_id,claim_ref,kind,resolved,observed_at,pd,attrs,ledger_handle,supersedes,"sha256:"+digest(identity))
def rebind(record:EvidenceRecord,claim_ref:str)->EvidenceRecord:return make_record(task_id=record.task_id,claim_ref=claim_ref,kind=record.kind,observed_at=record.observed_at,payload={"rebound_from":record.record_id,"payload_digest":record.payload_digest},attributes=dict(record.attributes),ledger_handle=record.ledger_handle)
@dataclass(frozen=True)
class Clause:
    clause_id:str; predicate:str="ALL_OF"; min_grade:str=OBSERVED; required_kinds:tuple[str,...]=(); expect:str|None=None; negative:bool=False
@dataclass(frozen=True)
class CompletionContract:
    task_id:str; boundary:date; clauses:tuple[Clause,...]; admits_assertion:bool=False
@dataclass(frozen=True)
class Warrant:
    task_id:str; status:str; satisfied:tuple[str,...]=(); unsatisfied:tuple[tuple[str,tuple[str,...]],...]=(); grade_shortfalls:tuple[str,...]=(); unbound_records:tuple[tuple[str,str],...]=(); inadmissible_records:tuple[str,...]=(); asserted_only_clauses:tuple[str,...]=(); superseded_chains:tuple[str,...]=(); adjudicated_evidence_ids:tuple[str,...]=()
    def reason_codes(self)->tuple[str,...]:
        codes=set()
        for _,rs in self.unsatisfied:codes.update(rs)
        return tuple(sorted(codes))
def validate_contract(contract:CompletionContract)->None:
    if not contract.task_id:raise ContractError("Contract has no task_id")
    if not contract.clauses:raise ContractError("Contract has no clauses; a vacuous contract cannot be satisfied")
    seen=set()
    for c in contract.clauses:
        if not c.clause_id:raise ContractError("Clause has no clause_id")
        if c.clause_id in seen:raise ContractError(f"Duplicate clause_id: {c.clause_id}")
        seen.add(c.clause_id)
        if c.predicate not in PREDICATES:raise ContractError(f"Unknown predicate: {c.predicate}")
        if c.min_grade not in GRADE:raise ContractError(f"Unknown provenance grade: {c.min_grade}")
        if c.predicate in ("ALL_OF","ANY_OF") and not c.required_kinds:raise ContractError(f"Clause {c.clause_id} using {c.predicate} must declare required_kinds")
        for k in c.required_kinds:
            if k not in PROVENANCE_BY_KIND:raise ContractError(f"Unknown evidence kind: {k}")
        if GRADE[c.min_grade]<=GRADE[ASSERTED] and not contract.admits_assertion:raise ContractError(f"Clause {c.clause_id} admits executor assertion; set admits_assertion=True to declare that explicitly")
        if c.negative and c.predicate!="NONE_FAILED":raise ContractError(f"Negative clause {c.clause_id} must use predicate NONE_FAILED")
        if c.predicate in ("DIGEST_MATCHES","REF_ADVANCED","COVERS") and not c.expect:raise ContractError(f"Clause {c.clause_id} predicate {c.predicate} needs expect")
def _predicate_holds(c:Clause,rs:tuple[EvidenceRecord,...])->bool:
    if c.predicate=="ALL_OF":return bool(rs)
    if c.predicate=="ANY_OF":return any(r.kind in c.required_kinds for r in rs)
    if c.predicate=="EXIT_ZERO":return any(r.kind=="PROCESS_EXIT" and r.attr("exit_code")=="0" for r in rs)
    if c.predicate=="NONEMPTY_STREAM":return any(r.kind=="STREAM_DIGEST" and r.attr("empty")=="false" for r in rs)
    if c.predicate=="DIGEST_MATCHES":return any(r.payload_digest==c.expect for r in rs)
    if c.predicate=="REF_ADVANCED":return any(r.kind=="VCS_REF" and r.attr("ref")!=c.expect and r.attr("dirty")=="false" for r in rs)
    if c.predicate=="COVERS":return any(r.kind=="COVERAGE_SCOPE" and r.attr("scope")==c.expect for r in rs)
    if c.predicate=="NONE_FAILED":return not any(r.attr("status")=="FAIL" for r in rs)
    raise ContractError(f"Unknown predicate: {c.predicate}")
def adjudicate(contract:CompletionContract,records:Iterable[EvidenceRecord],*,delivered_handles:Iterable[str]=())->Warrant:
    validate_contract(contract);delivered=set(delivered_handles);all_records=tuple(sorted({r.record_id:r for r in records}.values(),key=lambda r:r.record_id));usable=[];unbound=[];inadmissible=[];excluded={};well=[]
    def exclude(r,reason):excluded.setdefault(r.claim_ref,set()).add(reason)
    for r in all_records:
        if PROVENANCE_BY_KIND.get(r.kind)!=r.provenance:unbound.append((r.record_id,KIND_PROVENANCE_MISMATCH));exclude(r,KIND_PROVENANCE_MISMATCH);continue
        well.append(r)
        if r.task_id!=contract.task_id:unbound.append((r.record_id,TASK_MISMATCH));exclude(r,TASK_MISMATCH);continue
        if r.ledger_handle is not None and r.ledger_handle not in delivered:unbound.append((r.record_id,UNDELIVERED));exclude(r,UNDELIVERED);continue
        if date.fromisoformat(r.observed_at[:10])>contract.boundary:inadmissible.append(r.record_id);exclude(r,TEMPORALLY_INADMISSIBLE);continue
        usable.append(r)
    usable_ids={r.record_id for r in usable};superseded_ids={r.supersedes for r in well if r.supersedes};unresolved=set();chains=[];by_id={r.record_id:r for r in well}
    for r in well:
        if not r.supersedes:continue
        prior=by_id.get(r.supersedes)
        if prior is None:continue
        if r.record_id not in usable_ids or GRADE[r.provenance]<GRADE[prior.provenance]:unresolved.add(r.claim_ref);chains.append(f"{r.supersedes}->{r.record_id}")
    active=tuple(r for r in usable if r.record_id not in superseded_ids);satisfied=[];unsatisfied=[];short=[];asserted=[]
    for c in contract.clauses:
        reasons=_evaluate_clause(c,active,all_records,unresolved,excluded.get(c.clause_id,set()))
        if GRADE_SHORTFALL in reasons or ASSERTION_ONLY in reasons:short.append(c.clause_id)
        if not reasons:
            satisfied.append(c.clause_id);candidates=[r for r in active if r.claim_ref==c.clause_id];best=max((GRADE[r.provenance] for r in candidates),default=0)
            if best==GRADE[ASSERTED]:asserted.append(c.clause_id)
        else:unsatisfied.append((c.clause_id,tuple(sorted(reasons))))
    status=DONE if not unsatisfied else BLOCKED if all(set(rs)=={EVIDENCE_UNAVAILABLE} for _,rs in unsatisfied) else NOT_DONE
    return Warrant(contract.task_id,status,tuple(satisfied),tuple(unsatisfied),tuple(sorted(short)),tuple(sorted(unbound)),tuple(sorted(inadmissible)),tuple(sorted(asserted)),tuple(sorted(chains)),tuple(sorted(r.record_id for r in active)))
def _evaluate_clause(c,active,all_records,unresolved,excluded_reasons):
    if c.clause_id in unresolved:return {SUPERSEDED_UNRESOLVED}
    candidates=tuple(r for r in active if r.claim_ref==c.clause_id);evidential=tuple(r for r in candidates if r.kind!="UNAVAILABLE_NOTICE")
    if not evidential:
        if excluded_reasons:return set(excluded_reasons)
        if any(r.claim_ref==c.clause_id and r.kind=="UNAVAILABLE_NOTICE" for r in all_records):return {EVIDENCE_UNAVAILABLE}
        return {MISSING_EVIDENCE}
    reasons=set();kinds={r.kind for r in evidential}
    if c.predicate=="ALL_OF" and any(k not in kinds for k in c.required_kinds):reasons.add(WRONG_KIND)
    elif c.predicate=="ANY_OF" and not any(k in kinds for k in c.required_kinds):reasons.add(WRONG_KIND)
    best=max(GRADE[r.provenance] for r in evidential)
    if best<GRADE[c.min_grade]:reasons.add(ASSERTION_ONLY if best==GRADE[ASSERTED] else GRADE_SHORTFALL)
    if c.negative and not any(r.kind=="COVERAGE_SCOPE" for r in evidential):reasons.add(NEGATIVE_WITHOUT_COVERAGE)
    if not _predicate_holds(c,evidential):reasons.add(PREDICATE_UNSATISFIED)
    return reasons
def explain(warrant:Warrant)->str:
    lines=[f"task: {warrant.task_id}",f"status: {warrant.status}"]
    for c in warrant.satisfied:lines.append(f"  SATISFIED   {c}")
    for c,rs in warrant.unsatisfied:lines.append(f"  UNSATISFIED {c}: {', '.join(rs)}")
    for rid,reason in warrant.unbound_records:lines.append(f"  UNBOUND     {rid}: {reason}")
    for rid in warrant.inadmissible_records:lines.append(f"  INADMISSIBLE {rid}")
    for chain in warrant.superseded_chains:lines.append(f"  SUPERSEDED  {chain}")
    for c in warrant.asserted_only_clauses:lines.append(f"  ASSERTION   {c} rests on executor assertion only")
    return "\n".join(lines)
def seal(warrant:Warrant)->str:
    return "sha256:"+digest({"task_id":warrant.task_id,"status":warrant.status,"satisfied":list(warrant.satisfied),"unsatisfied":[[c,list(r)] for c,r in warrant.unsatisfied],"grade_shortfalls":list(warrant.grade_shortfalls),"unbound_records":[list(u) for u in warrant.unbound_records],"inadmissible_records":list(warrant.inadmissible_records),"asserted_only_clauses":list(warrant.asserted_only_clauses),"superseded_chains":list(warrant.superseded_chains)})
