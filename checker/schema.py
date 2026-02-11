from __future__ import annotations


def json_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Password Strength Checker Output",
        "oneOf": [
            {"$ref": "#/$defs/result"},
            {"$ref": "#/$defs/batch"},
        ],
        "$defs": {
            "check": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "passed": {"type": "boolean"},
                    "message": {"type": "string"},
                },
                "required": ["name", "passed", "message"],
            },
            "breakdown": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "length_score": {"type": "integer"},
                    "diversity_bonus": {"type": "integer"},
                    "penalties": {
                        "type": "object",
                        "additionalProperties": {"type": "integer"},
                    },
                    "capped": {"type": "boolean"},
                    "cap": {"type": ["integer", "null"]},
                    "cap_reason": {"type": ["string", "null"]},
                },
                "required": [
                    "length_score",
                    "diversity_bonus",
                    "penalties",
                    "capped",
                    "cap",
                    "cap_reason",
                ],
            },
            "metrics": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "sequence_found": {"type": "boolean"},
                    "keyboard_sequence": {"type": "boolean"},
                    "repeated_segment": {"type": "boolean"},
                    "repeat_len": {"type": "integer"},
                    "is_common": {"type": "boolean"},
                    "has_dictionary_word": {"type": "boolean"},
                },
                "required": [
                    "sequence_found",
                    "keyboard_sequence",
                    "repeated_segment",
                    "repeat_len",
                    "is_common",
                    "has_dictionary_word",
                ],
            },
            "result": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "version": {"type": "integer"},
                    "ruleset": {"type": "string"},
                    "profile": {"type": "string"},
                    "policy": {"type": "string"},
                    "score": {"type": "integer"},
                    "label": {"type": "string"},
                    "length": {"type": "integer"},
                    "category_count": {"type": "integer"},
                    "min_length": {"type": "integer"},
                    "checks": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/check"},
                    },
                    "suggestions": {"type": "array", "items": {"type": "string"}},
                    "entropy_estimate": {"type": ["number", "null"]},
                    "score_breakdown": {"$ref": "#/$defs/breakdown"},
                    "metrics": {"$ref": "#/$defs/metrics"},
                    "index": {"type": "integer"},
                },
                "required": [
                    "version",
                    "ruleset",
                    "profile",
                    "policy",
                    "score",
                    "label",
                    "length",
                    "category_count",
                    "min_length",
                    "checks",
                    "suggestions",
                    "entropy_estimate",
                ],
            },
            "batch": {
                "type": "array",
                "items": {"$ref": "#/$defs/result"},
            },
        },
    }
