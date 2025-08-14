import pytest

# NOTE: These are scaffolds for Day 5. We'll wire real client + app in Day 6.
# Keep them as intent-capturing placeholders so CI doesn't fail.

@pytest.mark.skip(reason="scaffold: implement when POST /v1/plays exists (Day 6)")
def test_create_play_ok_https_mp4_returns_201_and_location_header():
    """
    Happy path:
      - title: non-empty
      - video_path: https URL ending with .mp4
    Expect:
      - 201 Created
      - 'Location' header set to /v1/plays/{id}
    """
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_422_empty_title():
    """Empty/whitespace-only title → 422.title"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_422_http_scheme_rejected():
    """video_path uses http:// → 422.video_path"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_422_unsupported_extension_avi():
    """video_path ends with .avi → 422.video_path"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_422_local_file_path_rejected_when_override_off():
    """file:// path rejected when ALLOW_LOCAL_VIDEO_PATHS is false → 422.video_path"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_422_relative_path_rejected_when_override_off():
    """relative path rejected when ALLOW_LOCAL_VIDEO_PATHS is false → 422.video_path"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_ok_file_scheme_allowed_with_override():
    """file:// path accepted when ALLOW_LOCAL_VIDEO_PATHS is true → 201 + Location"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_ok_relative_under_media_root_with_override():
    """relative path under MEDIA_ROOT accepted when override is true → 201 + Location"""
    pass

@pytest.mark.skip(reason="scaffold: implement with validation on Day 6")
def test_create_play_trims_inputs_before_validation():
    """Leading/trailing whitespace is trimmed before rules apply."""
    pass
