from wiki_scraper import main


def test_smoke():
    assert True

def test_cli_parses_and_runs_for_unimplemented_mode():
    # Should raise NotImplementedError for now
    try:
        main(["Pikachu", "--summary"])
        assert False, "Expected NotImplementedError"
    except NotImplementedError:
        assert True