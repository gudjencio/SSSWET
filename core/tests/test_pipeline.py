from ssswet_core.pipeline import ResearchPipeline


def test_pipeline_decomposes_and_records_independent_work_units():
    pipeline = ResearchPipeline()
    task_id, steps = pipeline.start("Study a harmless mathematical optimization problem", "math")

    assert task_id
    assert len(steps) == 2
    assert steps[0].subtask.role == "mathematician"
    assert steps[1].subtask.role == "independent_verifier"
    assert all(step.provider == "deterministic-demo" for step in steps)
