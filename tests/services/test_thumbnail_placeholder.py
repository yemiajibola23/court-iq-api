from app.services.thumbnail_placeholder import build_placeholder

def test_build_placeholder_static_returns_configured_url(set_env_and_reload):    
    assert build_placeholder(play=object(), mode="static", static_url="/static/img/ph.png") == "/static/img/ph.png"

def test_build_placeholder_off_returns_none():
    assert build_placeholder(play=object(), mode="off", static_url="/static/img/ph.png") == None
