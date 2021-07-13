import pytest


@pytest.mark.skip(reason="Not fully implemented")
@pytest.mark.parametrize(
    "job_tags, search_tags, mode, get_id, del_id",
    (
        [[{}], {"a"}, any, None, None],
        # [None],
        # [{"test", "fast"}, {"fast"}],
    ),
)
def test_sch_tags(job_tags, search_tags, mode, get_id, del_id):
    ...
    # sch.delete_jobs({"a","b"},mode=all)
    # sch.delete_jobs({"a","b"},mode=any)
    # sch.delete_jobs({},mode=all) # => delete_all_jobs
    # sch.delete_jobs({},mode=any) # => delete_all_jobs
    # sch.delete_jobs(mode=any) # => delete_all_jobs
    # sch.delete_jobs(mode=all) # => delete_all_jobs
    # sch.delete_jobs() # => delete_all_jobs
