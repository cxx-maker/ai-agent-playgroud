from typing import TypedDict, List, Optional


class InterviewState(TypedDict):
    messages: List[dict]
    resume_text: str
    jd_text: str
    company_name: str
    job_title: str
    selected_function: Optional[str]
    function_result: str
