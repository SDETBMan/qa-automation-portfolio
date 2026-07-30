"""Tests for the selector extractor module."""

from monitor.extractor import extract_from_html, extract_from_js, build_snapshot


class TestExtractFromHtml:
    def test_extracts_ids(self):
        html = '<div id="user-name"></div><input id="password" />'
        result = extract_from_html(html)
        assert "user-name" in result["ids"]
        assert "password" in result["ids"]

    def test_extracts_classes(self):
        html = '<div class="inventory_item cart_item"></div>'
        result = extract_from_html(html)
        assert "inventory_item" in result["classes"]
        assert "cart_item" in result["classes"]

    def test_extracts_data_test(self):
        html = '<div data-test="error"></div><select data-test="product-sort-container"></select>'
        result = extract_from_html(html)
        assert "error" in result["data_test"]
        assert "product-sort-container" in result["data_test"]

    def test_empty_html(self):
        result = extract_from_html("")
        assert result["ids"] == set()
        assert result["classes"] == set()
        assert result["data_test"] == set()

    def test_no_relevant_attributes(self):
        html = "<div><span>Hello</span></div>"
        result = extract_from_html(html)
        assert result["ids"] == set()
        assert result["classes"] == set()
        assert result["data_test"] == set()


class TestExtractFromJs:
    def test_extracts_getelementbyid(self):
        js = 'document.getElementById("user-name")'
        result = extract_from_js(js)
        assert "user-name" in result["ids"]

    def test_extracts_queryselector_id(self):
        js = "document.querySelector('#login-button')"
        result = extract_from_js(js)
        assert "login-button" in result["ids"]

    def test_extracts_queryselector_class(self):
        js = "document.querySelector('.inventory_item')"
        result = extract_from_js(js)
        assert "inventory_item" in result["classes"]

    def test_extracts_classname(self):
        js = 'className="inventory_item_name"'
        result = extract_from_js(js)
        assert "inventory_item_name" in result["classes"]

    def test_extracts_data_test_jsx(self):
        js = 'data-test="error"'
        result = extract_from_js(js)
        assert "error" in result["data_test"]

    def test_empty_js(self):
        result = extract_from_js("")
        assert result["ids"] == set()
        assert result["classes"] == set()
        assert result["data_test"] == set()


class TestBuildSnapshot:
    def test_merges_and_deduplicates(self):
        html_sel = {
            "ids": {"user-name", "password"},
            "classes": {"inventory_item"},
            "data_test": {"error"},
        }
        js_sel = {
            "ids": {"user-name", "login-button"},
            "classes": {"cart_item"},
            "data_test": {"error", "checkout"},
        }
        snapshot = build_snapshot(html_sel, js_sel, "https://www.saucedemo.com", "/assets/index-abc.js")

        assert "user-name" in snapshot["ids"]
        assert "password" in snapshot["ids"]
        assert "login-button" in snapshot["ids"]
        assert "inventory_item" in snapshot["classes"]
        assert "cart_item" in snapshot["classes"]
        assert "error" in snapshot["data_test"]
        assert "checkout" in snapshot["data_test"]
        assert snapshot["url"] == "https://www.saucedemo.com"
        assert snapshot["meta"]["js_bundle_url"] == "/assets/index-abc.js"
        assert "timestamp" in snapshot

    def test_snapshot_lists_are_sorted(self):
        html_sel = {"ids": {"z-id", "a-id"}, "classes": set(), "data_test": set()}
        js_sel = {"ids": set(), "classes": set(), "data_test": set()}
        snapshot = build_snapshot(html_sel, js_sel, "https://example.com")
        assert snapshot["ids"] == ["a-id", "z-id"]
