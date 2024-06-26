t = {

    "query": {
        "function_score": {
            "query": {
                "bool": {
                    "should": [
                        {
                            "bool": {
                                "should": [
                                    {"dis_max": {
                                        "queries": [
                                            {"constant_score": {
                                                "filter": {
                                                    "match_phrase": {
                                                        "primary_field": "Скоро откроется дачный сезон"
                                                    }
                                                },
                                                "boost": 10
                                            }},
                                            {"constant_score": {
                                                "filter": {
                                                    "match_phrase": {
                                                        "secondary_field": "Скоро откроется дачный сезон"
                                                    }
                                                },
                                                "boost": 10
                                            }}
                                        ]
                                    }}
                                ]
                            }
                        }
                    ]
                }
            },
            "functions": [
                {"field_value_factor": {"field": "rating", "modifier": "ln2p", "missing": 1}}]

        }

    },

    "highlight": {"fields": {"primary_field": {"phrase_limit": 100, "pre_tags": ["<bold>"], "post_tags": ["</bold>"]}}},
    "suggest": {
        "spellcheck": {
            "text": "Скоро откроется дачный сезон",
            "phrase": {"field": "primary_field.trigram", "size": 1, "gram_size": 3,
                       "direct_generator": [{"field": "primary_field.trigram"}], "collate": {
                    "query": {"source": {"match_phrase": {"primary_field": "{{suggestion}}"}}}
                }}
        }
    }

}
