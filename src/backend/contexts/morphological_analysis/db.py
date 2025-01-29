"""DB client to retrieve lexicometric information within the QWB-API.
"""

import typing as t
from backend.tools.sql_client import SQLClient


class MorphologicalAnalysisClient(SQLClient):
    """Manipulate textual data from the SQL database."""

    def morphological_analysis_reading_query(self, word_reading_ids: t.List[str]):
        """Build SQL query to retrieve morphological analysis data given a set of word_reading_ids."""
        return self.format_query(
            f"""
                SELECT
                    `language_lemma_form`.`lemma_form` AS `lemma`,
                    `word_class`.`string` AS `word_class`,
                    trim(regexp_replace(`language_lemma`.`main_meaning`, '^[# ]+', '')) AS `short_definition`,
                    `language_lemma_form`.`supplement` AS `root_designation`,
                    `verbal_stem`.`string` AS `verb_stem`,
                    `verbal_tempus`.`string` AS `verb_tense`,
                    `person`.`string` AS `person`,
                    `gender`.`string` AS `gender`,
                    `number`.`string` AS `number`,
                    `status`.`string` AS `state`,
                    `augment`.`string` AS `augment`,
                    `suffix_person`.`string` AS `suffix_person`,
                    `suffix_gender`.`string` AS `suffix_gender`,
                    `suffix_number`.`string` AS `suffix_number`
            FROM `language_sign_cluster_reading_parsing`
                JOIN `language_lemma` ON `language_sign_cluster_reading_parsing`.`language_lemma_id` = `language_lemma`.`language_lemma_id`
                JOIN `language_lemma_form` ON `language_lemma_form`.`language_lemma_id` = `language_lemma`.`language_lemma_id`
                        AND `language_lemma_form`.`is_main` = 1
                JOIN `language_word_class` ON `language_lemma`.`language_word_class_id` = `language_word_class`.`language_word_class_id`
                JOIN `i18n_view_localized_string` `word_class` ON `word_class`.`string_id` = `language_word_class`.`i18n_string_id`
                        AND `word_class`.`language_id` = COALESCE(
                                (SELECT `language_id`
                                FROM `i18n_view_language`
                                WHERE `i18n_view_language`.`iso_639_1` = 1
                                LIMIT 1),
                                1
                            )

                LEFT JOIN (
                    `language_verbal_stem` `lvs`
                    JOIN `i18n_localized_string` `verbal_stem` ON `verbal_stem`.`i18n_localized_string_id` = `lvs`.`i18n_string_id`
                ) ON `lvs`.`language_verbal_stem_id` = `language_sign_cluster_reading_parsing`.`language_verbal_stem_id`
                    AND `verbal_stem`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_verbal_tempus_definition` `ltd`
                    JOIN `i18n_localized_string` `verbal_tempus` ON `verbal_tempus`.`i18n_localized_string_id` = `ltd`.`i18n_string_id`
                ) ON `ltd`.`language_verbal_tempus_definition_id` = `language_sign_cluster_reading_parsing`.`verbal_tempus`
                    AND `verbal_tempus`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_person_definition` `lpd`
                    JOIN `i18n_localized_string` `person` ON `person`.`i18n_localized_string_id` = `lpd`.`i18n_string_id`
                ) ON `lpd`.`language_person_definition_id` = `language_sign_cluster_reading_parsing`.`person`
                    AND `person`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_gender_definition` `lgd`
                    JOIN `i18n_localized_string` `gender` ON `gender`.`i18n_localized_string_id` = `lgd`.`i18n_string_id`
                ) ON `lgd`.`language_gender_definition_id` = `language_sign_cluster_reading_parsing`.`gender`
                    AND `gender`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_number_definition` `lnd`
                    JOIN `i18n_localized_string` `number` ON `number`.`i18n_localized_string_id` = `lnd`.`i18n_string_id`
                ) ON `language_sign_cluster_reading_parsing`.`number` = `lnd`.`language_number_definition_id`
                    AND `number`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_status_definition` `lsd`
                    JOIN `i18n_localized_string` `status` ON `status`.`i18n_localized_string_id` = `lsd`.`i18n_string_id`
                ) ON `language_sign_cluster_reading_parsing`.`status` = `lsd`.`language_status_definition_id`
                    AND `status`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_augment_definition` `lad`
                    JOIN `i18n_localized_string` `augment` ON `augment`.`i18n_localized_string_id` = `lad`.`i18n_string_id`
                ) ON `language_sign_cluster_reading_parsing`.`augment` = `lad`.`language_augment_definition_id`
                    AND `augment`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_person_definition` `lpsd`
                    JOIN `i18n_localized_string` `suffix_person` ON `suffix_person`.`i18n_localized_string_id` = `lpsd`.`i18n_string_id`
                ) ON `lpsd`.`language_person_definition_id` = `language_sign_cluster_reading_parsing`.`suffix_person`
                    AND `suffix_person`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_gender_definition` `lgsd`
                    JOIN `i18n_localized_string` `suffix_gender` ON `suffix_gender`.`i18n_localized_string_id` = `lgsd`.`i18n_string_id`
                ) ON `lgsd`.`language_gender_definition_id` = `language_sign_cluster_reading_parsing`.`suffix_gender`
                    AND `suffix_gender`.`i18n_language_id` = `word_class`.`language_id`

                LEFT JOIN (
                    `language_number_definition` `lnsd`
                    JOIN `i18n_localized_string` `suffix_number` ON `suffix_number`.`i18n_localized_string_id` = `lnsd`.`i18n_string_id`
                ) ON `lnsd`.`language_number_definition_id` = `language_sign_cluster_reading_parsing`.`suffix_number`
                    AND `suffix_number`.`i18n_language_id` = `word_class`.`language_id`

            WHERE `language_sign_cluster_reading_parsing`.`manuscript_sign_cluster_reading_id` IN ({','.join(word_reading_ids)})
            ORDER BY `language_sign_cluster_reading_parsing`.`element_sequence` ASC;
                """
        )

    def word_readings_query(
        self,
        word: str,
        manuscript: t.Optional[str] = None,
        column: t.Optional[str] = None,
        line: t.Optional[str] = None,
    ):
        """Given a word, build the request that returns all corresponding reading_ids."""
        query = f"""
                SELECT manuscript_sign_cluster_reading.manuscript_sign_cluster_reading_id, manuscript_view.manuscript, manuscript_view.column, manuscript_view.line, manuscript_view.sequence_in_line
                FROM manuscript_sign_cluster_reading
                JOIN manuscript_view
                WHERE manuscript_sign_cluster_reading.manuscript_sign_cluster_reading_id = manuscript_view.manuscript_sign_cluster_reading_id AND manuscript_sign_cluster_reading.reading='{word}'
                """
        if manuscript:
            query += f" AND manuscript_view.manuscript='{manuscript}'"
        if manuscript and column:
            query += f" AND manuscript_view.column='{column}'"
        if manuscript and column and line:
            query += f" AND manuscript_view.line='{line}'"

        return self.format_query(query)

    async def get_word_readings_query(
        self,
        word: str,
        manuscript: t.Optional[str] = None,
        column: t.Optional[str] = None,
        line: t.Optional[str] = None,
    ):
        """Given a word, returns the corresponding readings and their position in the manuscript."""
        return await self.database.fetch_all(
            query=self.word_readings_query(
                word=word, manuscript=manuscript, column=column, line=line
            )
        )

    async def get_word_morphological_analysis(
        self,
        word: str,
        manuscript: t.Optional[str] = None,
        column: t.Optional[str] = None,
        line: t.Optional[str] = None,
    ):
        """Given a word, return all corresponding morphological analysis."""
        word_readings_results = await self.get_word_readings_query(
            word=word, manuscript=manuscript, column=column, line=line
        )
        word_readings_info = [dict(result) for result in word_readings_results]
        reading_ids = [
            str(dict(reading)["manuscript_sign_cluster_reading_id"])
            for reading in word_readings_info
        ]
        if not reading_ids:
            return []
        else:
            morphological_results = await self.database.fetch_all(
                query=self.morphological_analysis_reading_query(
                    word_reading_ids=reading_ids
                )
            )
            # Flatten query results into a dictionary
            morphological_info = [dict(result) for result in morphological_results]
            results = []

            for word_reading_info in word_readings_info:
                results.append({"position": word_reading_info})
                for morphological_result in morphological_info:
                    results.append({"morphological_analysis": morphological_result})

            return results
