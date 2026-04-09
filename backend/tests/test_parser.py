"""Exhaustive parser tests. 20+ cases covering every format and edge case."""
from __future__ import annotations

from datetime import datetime

from app.core.parser import parse_chat


def _one(text: str):
    return parse_chat(text).messages


def test_basic_user_message_dmy_12h():
    msgs = _one("18/04/25, 10:00 am - Alice: hello")
    assert len(msgs) == 1
    assert msgs[0].user == "Alice"
    assert msgs[0].message == "hello"
    assert msgs[0].datetime == datetime(2025, 4, 18, 10, 0)


def test_dmy_24h():
    msgs = _one("18/04/2025, 14:30 - Bob: evening")
    assert msgs[0].datetime == datetime(2025, 4, 18, 14, 30)
    assert msgs[0].user == "Bob"


def test_narrow_nbsp_before_ampm():
    # \u202f is the actual char WhatsApp uses
    msgs = _one("18/04/25, 11:30\u202fam - Alice: hi")
    assert msgs and msgs[0].hour == 11 and msgs[0].user == "Alice"


def test_regular_nbsp_before_ampm():
    msgs = _one("18/04/25, 11:30\u00a0pm - Alice: hi")
    assert msgs and msgs[0].hour == 23


def test_mm_dd_yyyy_format():
    # second component 30 → must be day → layout = mdy NO (30 as day means first=month).
    # With "04/30/25" the second component is 30 > 12 → mdy detected.
    msgs = _one("04/30/25, 9:00 am - Carol: hey")
    assert msgs[0].datetime == datetime(2025, 4, 30, 9, 0)


def test_system_message_joined():
    msgs = _one("18/04/25, 9:04 am - +91 97852 54150 joined using this group's invite link")
    assert len(msgs) == 1
    m = msgs[0]
    assert m.message_type == "system"
    assert m.event_type == "join"
    assert m.user is None


def test_system_message_left():
    msgs = _one("18/04/25, 9:05 am - +91 96605 90520 left")
    assert msgs[0].event_type == "leave"


def test_tilde_prefixed_actor_left():
    msgs = _one("18/04/25, 10:49 am - ~ Hetvi Doshi left")
    assert msgs[0].message_type == "system"
    assert msgs[0].event_type == "leave"


def test_you_removed_event():
    msgs = _one("10/04/25, 7:05 pm - You removed Nishu")
    assert msgs[0].event_type == "remove"
    assert msgs[0].message_type == "system"


def test_group_rename_extracts_name():
    text = "18/04/25, 9:39 am - You changed the group name from \"Old\" to \"New\""
    chat = parse_chat(text)
    assert chat.metadata.group_name == "New"
    assert chat.messages[0].event_type == "group_change"


def test_encryption_notice():
    msgs = _one("10/04/25, 11:41 am - Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.")
    assert msgs[0].event_type == "encrypt_notice"


def test_created_this_group():
    msgs = _one("10/04/25, 11:41 am - You created this group")
    assert msgs[0].event_type == "group_change"


def test_multiline_message_continuation():
    text = (
        "18/04/25, 10:00 am - Alice: line 1\n"
        "line 2\n"
        "line 3\n"
        "18/04/25, 10:05 am - Bob: reply"
    )
    msgs = _one(text)
    assert len(msgs) == 2
    assert msgs[0].message == "line 1\nline 2\nline 3"
    assert msgs[1].user == "Bob"


def test_message_with_colon_in_content():
    msgs = _one("18/04/25, 10:00 am - Alice: check this: https://example.com/x")
    assert msgs[0].user == "Alice"
    assert msgs[0].message == "check this: https://example.com/x"
    assert msgs[0].urls == ["https://example.com/x"]


def test_media_omitted():
    msgs = _one("18/04/25, 10:00 am - Alice: <Media omitted>")
    assert msgs[0].is_media is True
    assert msgs[0].word_count == 0


def test_deleted_message():
    msgs = _one("18/04/25, 10:00 am - Alice: This message was deleted")
    assert msgs[0].is_deleted is True


def test_emoji_extraction():
    msgs = _one("18/04/25, 10:00 am - Alice: love it \U0001F60D\U0001F389")
    assert len(msgs[0].emoji_list) == 2


def test_url_and_mention():
    msgs = _one("18/04/25, 10:00 am - Alice: hey @bob see https://x.com")
    assert msgs[0].has_mention is True
    assert msgs[0].urls == ["https://x.com"]


def test_malformed_line_is_counted_as_error_when_no_prior():
    chat = parse_chat("this line has no timestamp at all")
    assert chat.metadata.parse_errors == 1
    assert chat.metadata.total_messages == 0


def test_phone_number_user_is_captured_as_user_when_has_colon():
    # User messages can come from phone-number-style names
    msgs = _one("18/04/25, 10:00 am - +91 90470 61221: hello world")
    assert msgs[0].message_type == "user"
    assert msgs[0].user == "+91 90470 61221"


def test_long_message_stable():
    body = "a" * 10000
    msgs = _one(f"18/04/25, 10:00 am - Alice: {body}")
    assert msgs[0].char_count == len(body)


def test_mixed_user_and_system_counts_correctly():
    text = (
        "10/04/25, 11:41 am - You created this group\n"
        "18/04/25, 9:04 am - +91 97852 54150 joined using this group's invite link\n"
        "18/04/25, 9:05 am - +91 97852 54150 left\n"
        "18/04/25, 10:00 am - Alice: hello everyone\n"
        "18/04/25, 10:05 am - Bob: hi alice\n"
    )
    chat = parse_chat(text)
    assert chat.metadata.total_system_events == 3
    assert chat.metadata.total_user_messages == 2
    assert chat.metadata.total_messages == 5


def test_real_data_sample_parses_without_dropping_events():
    # Mirrors the spec's expectation on the real Data.txt sample
    text = "\n".join([
        "10/04/25, 11:41 am - Messages and calls are end-to-end encrypted.",
        "10/04/25, 11:41 am - You created this group",
        "10/04/25, 4:45 pm - Mahima JIO changed this group's icon",
        "18/04/25, 9:04 am - +91 97852 54150 joined using this group's invite link",
        "18/04/25, 9:04 am - +91 97852 54150 left",
        "18/04/25, 10:49 am - ~ Hetvi Doshi left",
        "18/04/25, 11:00 am - Alice: hello",
    ])
    chat = parse_chat(text)
    assert chat.metadata.total_messages == 7
    assert chat.metadata.total_system_events == 6
    assert chat.metadata.total_user_messages == 1
