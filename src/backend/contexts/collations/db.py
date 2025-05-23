"""DB client to fetch textual data from the QWB API.
"""
import re
from typing import Optional
from backend.tools.sql_client import SQLClient
from collatex import Collation, collate
from collatex.core_classes import create_table_visualization
from .models import FOLLOWED_BY_MAPPER, FRAGMENTATION_PLACEHOLDER
from .utils import strip_hebrew_vowels


class ParallelsClient(SQLClient):
    """Manipulate textual data from the QWB API.
    """

    def parallel_query(self,
                       name: str,
                       chapter: Optional[str] = None,
                       verse: Optional[str] = None):
        """
        Build the query to retrieve parallels.
        """
        if chapter:
            if verse:
                return self.format_query(f"""
                    SELECT par_mv.manuscript
                            , par_mv.`column`
                            , par_mv.line
                            , par_mv.reading
                            , par_mv.followed_by
                    FROM manuscript_view mv
                    JOIN parallel_phrase_group_view
                        ON parallel_phrase_group_view.anchor_reading_id = mv.manuscript_sign_cluster_reading_id
                            AND parallel_phrase_group_view.anchor_reading_id != parallel_phrase_group_view.manuscript_sign_cluster_reading_id 
                    JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                    WHERE mv.manuscript = '{name}' AND mv.`column` = '{chapter}' AND mv.line = '{verse}';
                    """)
            return self.format_query(f"""
                    SELECT par_mv.manuscript
                            , par_mv.`column`
                            , par_mv.line
                            , par_mv.reading
                            , par_mv.followed_by
                    FROM manuscript_view mv
                    JOIN parallel_phrase_group_view
                        ON parallel_phrase_group_view.anchor_reading_id = mv.manuscript_sign_cluster_reading_id
                            AND parallel_phrase_group_view.anchor_reading_id != parallel_phrase_group_view.manuscript_sign_cluster_reading_id 
                    JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                    WHERE mv.manuscript = '{name}' AND mv.`column` = '{chapter}';
                """)
        return self.format_query(f"""
                    SELECT par_mv.manuscript
                            , par_mv.`column`
                            , par_mv.line
                            , par_mv.reading
                            , par_mv.followed_by
                    FROM manuscript_view mv
                    JOIN parallel_phrase_group_view
                        ON parallel_phrase_group_view.anchor_reading_id = mv.manuscript_sign_cluster_reading_id
                            AND parallel_phrase_group_view.anchor_reading_id != parallel_phrase_group_view.manuscript_sign_cluster_reading_id 
                    JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                    WHERE mv.manuscript = '{name}';""")

    def parallel_query_ordered(self,
                       name: str,
                       chapter: Optional[str] = None,
                       verse: Optional[str] = None):
        """Build the query to retrieve parallels in an ordered fashion.
        """
        if chapter:
            if verse:
                return self.format_query(f"""
                    WITH parallels AS (
                        SELECT    MIN(par_mv.unique_ordered_id) AS min_ordered_id
                                , MAX(par_mv.unique_ordered_id) AS max_ordered_id
                        FROM manuscript_view mv
                        JOIN parallel_phrase_group_view
                            ON parallel_phrase_group_view.anchor_reading_id = mv.manuscript_sign_cluster_reading_id
                                AND parallel_phrase_group_view.anchor_reading_id != parallel_phrase_group_view.manuscript_sign_cluster_reading_id 
                        JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                        WHERE mv.manuscript = '{name}' AND mv.`column` = '{chapter}' AND mv.line = '{verse}'
                        GROUP BY par_mv.manuscript_id
                    )

                    (
                        SELECT DISTINCT mv.manuscript
                                , mv.`column`
                                , mv.line
                                , mv.reading
                                , mv.followed_by
                                , parallel_phrase_group_view.anchor_reading_id
                                , mv.unique_ordered_id
                                , manuscript_sign_cluster.is_fully_reconstructed
                        FROM parallels
                            JOIN manuscript_view mv
                            ON mv.unique_ordered_id >= parallels.min_ordered_id
                                AND mv.unique_ordered_id <= parallels.max_ordered_id
                            LEFT JOIN parallel_phrase_group_view
                                ON parallel_phrase_group_view.manuscript_sign_cluster_reading_id = mv.manuscript_sign_cluster_reading_id
                            LEFT JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.anchor_reading_id
                            LEFT JOIN manuscript_sign_cluster ON manuscript_sign_cluster.manuscript_sign_cluster_id = mv.manuscript_sign_cluster_id
                        WHERE par_mv.manuscript = '{name}' AND par_mv.`column` = '{chapter}' AND par_mv.line = '{verse}'
                    )
                    UNION
                    (
                        SELECT DISTINCT   mv.manuscript
                                        , mv.`column`
                                        , mv.line
                                        , mv.reading
                                        , mv.followed_by
                                        , mv.manuscript_sign_cluster_reading_id
                                        , mv.unique_ordered_id
                                        , manuscript_sign_cluster.is_fully_reconstructed
                        FROM manuscript_view mv
                        LEFT JOIN manuscript_sign_cluster ON manuscript_sign_cluster.manuscript_sign_cluster_id = mv.manuscript_sign_cluster_id
                        WHERE mv.manuscript = '{name}' AND mv.`column` = '{chapter}' AND mv.line = '{verse}'
                    )
                    ORDER BY unique_ordered_id
                    ;
                    """
                                         )
            return self.format_query(f"""
                        WITH parallels AS (
                        SELECT    MIN(par_mv.unique_ordered_id) AS min_ordered_id
                                , MAX(par_mv.unique_ordered_id) AS max_ordered_id
                        FROM manuscript_view mv
                        JOIN parallel_phrase_group_view
                            ON parallel_phrase_group_view.anchor_reading_id = mv.manuscript_sign_cluster_reading_id
                                AND parallel_phrase_group_view.anchor_reading_id != parallel_phrase_group_view.manuscript_sign_cluster_reading_id 
                        JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                        WHERE mv.manuscript = '{name}' AND mv.`column` = '{chapter}'
                        GROUP BY par_mv.manuscript_id
                    )

                    (
                        SELECT DISTINCT mv.manuscript
                                , mv.`column`
                                , mv.line
                                , mv.reading
                                , mv.followed_by
                                , parallel_phrase_group_view.anchor_reading_id
                                , mv.unique_ordered_id,
                                , manuscript_sign_cluster.is_fully_reconstructed
                        FROM parallels
                            JOIN manuscript_view mv
                            ON mv.unique_ordered_id >= parallels.min_ordered_id
                                AND mv.unique_ordered_id <= parallels.max_ordered_id
                            LEFT JOIN parallel_phrase_group_view
                                ON parallel_phrase_group_view.manuscript_sign_cluster_reading_id = mv.manuscript_sign_cluster_reading_id
                            LEFT JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.anchor_reading_id
                            LEFT JOIN manuscript_sign_cluster ON manuscript_sign_cluster.manuscript_sign_cluster_id = mv.manuscript_sign_cluster_id
                        WHERE par_mv.manuscript = '{name}' AND par_mv.`column` = '{chapter}'
                    )
                    UNION
                    (
                        SELECT DISTINCT   mv.manuscript
                                        , mv.`column`
                                        , mv.line
                                        , mv.reading
                                        , mv.followed_by
                                        , mv.manuscript_sign_cluster_reading_id
                                        , mv.unique_ordered_id
                                        , manuscript_sign_cluster.is_fully_reconstructed
                        FROM manuscript_view mv
                        LEFT JOIN manuscript_sign_cluster ON manuscript_sign_cluster.manuscript_sign_cluster_id = mv.manuscript_sign_cluster_id
                        WHERE mv.manuscript = '{name}' AND mv.`column` = '{chapter}'
                    )
                    ORDER BY unique_ordered_id
                    ;
                    """)
        return self.format_query(f"""
                        WITH parallels AS (
                        SELECT    MIN(par_mv.unique_ordered_id) AS min_ordered_id
                                , MAX(par_mv.unique_ordered_id) AS max_ordered_id
                        FROM manuscript_view mv
                        JOIN parallel_phrase_group_view
                            ON parallel_phrase_group_view.anchor_reading_id = mv.manuscript_sign_cluster_reading_id
                                AND parallel_phrase_group_view.anchor_reading_id != parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                        JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.manuscript_sign_cluster_reading_id
                        WHERE mv.manuscript = '{name}'
                        GROUP BY par_mv.manuscript_id
                    )

                    (
                        SELECT DISTINCT mv.manuscript
                                , mv.`column`
                                , mv.line
                                , mv.reading
                                , mv.followed_by
                                , parallel_phrase_group_view.anchor_reading_id
                                , mv.unique_ordered_id
                                , manuscript_sign_cluster.is_fully_reconstructed
                        FROM parallels
                            JOIN manuscript_view mv
                            ON mv.unique_ordered_id >= parallels.min_ordered_id
                                AND mv.unique_ordered_id <= parallels.max_ordered_id
                            LEFT JOIN parallel_phrase_group_view
                                ON parallel_phrase_group_view.manuscript_sign_cluster_reading_id = mv.manuscript_sign_cluster_reading_id
                            LEFT JOIN manuscript_view par_mv ON par_mv.manuscript_sign_cluster_reading_id = parallel_phrase_group_view.anchor_reading_id
                            LEFT JOIN manuscript_sign_cluster ON manuscript_sign_cluster.manuscript_sign_cluster_id = mv.manuscript_sign_cluster_id
                        WHERE par_mv.manuscript = '{name}'
                    )
                    UNION
                    (
                        SELECT DISTINCT   mv.manuscript
                                        , mv.`column`
                                        , mv.line
                                        , mv.reading
                                        , mv.followed_by
                                        , mv.manuscript_sign_cluster_reading_id
                                        , mv.unique_ordered_id
                                        , manuscript_sign_cluster.is_fully_reconstructed
                        FROM manuscript_view mv
                        LEFT JOIN manuscript_sign_cluster ON manuscript_sign_cluster.manuscript_sign_cluster_id = mv.manuscript_sign_cluster_id                        WHERE mv.manuscript = '{name}'
                    )
                    ORDER BY unique_ordered_id;""")

    def mt_query(self,
                 name: str,
                 chapter: Optional[str] = None,
                 verse: Optional[str] = None):
        """Build the query to retrieve the Massoretic Text corresponding to the parallels.
        """
        if chapter:
            if verse:
                return self.format_query(f"""
                                    SELECT DISTINCT ms_A.reading, ms_A.followed_by, CONCAT("TM_", ms_A.manuscript) as manuscript
                                    from manuscript_view as ms_A
                                    left join parallel_phrase_group_view on anchor_reading_id = ms_A.manuscript_sign_cluster_reading_id
                                    left join parallel_word_of_phrase using(parallel_phrase_id)
                                    left join manuscript_view as ms_B on ms_B.manuscript_sign_cluster_reading_id=parallel_word_of_phrase.manuscript_sign_cluster_reading_id
                                    where ms_A.manuscript like '{name}'
                                    and  ms_A.`column` like '{chapter}'
                                    and  ms_A.line like '{verse}'
                                    and  ms_A.language_id=1
                                    and  ms_A.position_in_reference=0
                                    and  ms_B.language_id=1
                                    and  ms_B.position_in_reference=0;
                                    """)
            return self.format_query(f"""
                                    SELECT DISTINCT ms_A.reading, ms_A.followed_by, CONCAT("TM_", ms_A.manuscript) as manuscript
                                    from manuscript_view as ms_A
                                    left join parallel_phrase_group_view on anchor_reading_id = ms_A.manuscript_sign_cluster_reading_id
                                    left join parallel_word_of_phrase using(parallel_phrase_id)
                                    left join manuscript_view as ms_B on ms_B.manuscript_sign_cluster_reading_id=parallel_word_of_phrase.manuscript_sign_cluster_reading_id
                                    where ms_A.manuscript like '{name}'
                                    and  ms_A.`column` like '{chapter}'
                                    and  ms_A.language_id=1
                                    and  ms_A.position_in_reference=0
                                    and  ms_B.language_id=1
                                    and  ms_B.position_in_reference=0;
                                     """)
        return self.format_query(f"""
                        SELECT DISTINCT ms_A.reading, ms_A.followed_by, CONCAT("TM_", ms_A.manuscript) as manuscript
                        from manuscript_view as ms_A
                        left join parallel_phrase_group_view on anchor_reading_id = ms_A.manuscript_sign_cluster_reading_id
                        left join parallel_word_of_phrase using(parallel_phrase_id)
                        left join manuscript_view as ms_B on ms_B.manuscript_sign_cluster_reading_id=parallel_word_of_phrase.manuscript_sign_cluster_reading_id
                        where ms_A.manuscript like '{name}'
                        and  ms_A.language_id=1
                        and  ms_A.position_in_reference=0
                        and  ms_B.language_id=1
                        and  ms_B.position_in_reference=0;""")

    def count_parallels_query(self, name: str, chapter: Optional[str] = None):
        """SQL query to count the number of parallels per chapter.
        """
        if chapter:
            return self.format_query(f"""
            SELECT COUNT(DISTINCT ms_B.manuscript) as count_manuscript, ms_A.`line` as verse
                    from manuscript_view as ms_A
                    left join parallel_phrase_group_view on anchor_reading_id = ms_A.manuscript_sign_cluster_reading_id
                    left join parallel_word_of_phrase using(parallel_phrase_id)
                    left join manuscript_view as ms_B on ms_B.manuscript_sign_cluster_reading_id=parallel_word_of_phrase.manuscript_sign_cluster_reading_id
                    where ms_A.manuscript like '{name}'
                    and  ms_A.`column` like '{chapter}'
                    and  ms_A.language_id=1
                    and  ms_A.position_in_reference=0
                    and  ms_B.language_id=1
                    and  ms_B.position_in_reference=0
                    GROUP BY ms_A.`line`;
                    """)
        else:
            return self.format_query(f"""
            SELECT COUNT(DISTINCT ms_B.manuscript) as count_manuscript, ms_A.`column` as chapter
                    from manuscript_view as ms_A
                    left join parallel_phrase_group_view on anchor_reading_id = ms_A.manuscript_sign_cluster_reading_id
                    left join parallel_word_of_phrase using(parallel_phrase_id)
                    left join manuscript_view as ms_B on ms_B.manuscript_sign_cluster_reading_id=parallel_word_of_phrase.manuscript_sign_cluster_reading_id
                    where ms_A.manuscript like '{name}'
                    and  ms_A.language_id=1
                    and  ms_A.position_in_reference=0
                    and  ms_B.language_id=1
                    and  ms_B.position_in_reference=0
                    GROUP BY ms_A.`column`;""")
        
    @staticmethod
    def check_matched_bracket(word: str) -> bool:
        """Check if all opened bracket have been closed."""
        s = []
        balanced = True
        index = 0
        while index < len(word) and balanced:
            token = word[index]
            if token == "[":
                s.append(token)
            elif token == "]":
                if len(s) == 0:
                    balanced = False
                else:
                    s.pop()
            index += 1

        return balanced and len(s) == 0

    def unpack_parallel_data(self, records, reconstructed=False):
        """Unpack the manuscript data into a single string.
        If reconstructed is set to False, then remove all fully reconstructed readings
        as well as readings with either [ or ] and replace them with the fragment placeholder.
        """
        parallels = {}
        for record in records:
            if not reconstructed:
                if record["is_fully_reconstructed"]: #or "[" in record["reading"] or "]" in record["reading"]:
                    reading = FRAGMENTATION_PLACEHOLDER
                elif "[" in record["reading"] or "]" in record["reading"]:
                    bracket_word = record["reading"]
                    nbr_closed_brackets = bracket_word.count("]")
                    nbr_opened_brackets = bracket_word.count("[")
                    if nbr_closed_brackets < nbr_opened_brackets:  # if there is a missing closing
                        bracket_word = f"{bracket_word}]"
                    elif nbr_closed_brackets > nbr_opened_brackets:
                        bracket_word = f"[{bracket_word}"
                    elif not self.check_matched_bracket(record['reading']):
                        bracket_word = f"[{record['reading']}]"  # add brackets if they are missing
                    reading = re.sub(r'\[.*?\]', f'{FRAGMENTATION_PLACEHOLDER}', bracket_word)
                else:
                    reading = record["reading"]
            else:
                reading = record["reading"]
            try:
                parallels[record["manuscript"]] += reading +\
                    FOLLOWED_BY_MAPPER[record["followed_by"]]
            except KeyError:
                parallels[record["manuscript"]] = reading +\
                    FOLLOWED_BY_MAPPER[record["followed_by"]]
        return {man: context.strip() for man, context in parallels.items()}

    async def get_parallels(self,
                            name: str,
                            chapter: Optional[str] = None,
                            verse: Optional[str] = None):
        """Get all the parallels as a dictionary of manuscript name and text.
        """
        records = await self.database.fetch_all(query=self.parallel_query(name, chapter, verse))
        dict_records = list([dict(record) for record in records])
        filtered_dict_records = [{k: record[k] for k in ["manuscript", "column", "line"]} for record in dict_records]
        return [dict(t) for t in {tuple(d.items()) for d in filtered_dict_records}]

    async def get_parallels_content(self,
                                    name: str,
                                    reconstructed: bool,
                                    chapter: Optional[str] = None,
                                    verse: Optional[str] = None):
        """Get all the parallels as a list of text for a tradition, a chapter and a verse.
        If reconstructed is set to False, then reconstructed data is omitted from the parallel
        and replaced by the FRAG placeholder.
        """
        records = await self.database.fetch_all(query=self.parallel_query_ordered(name, chapter, verse))
        results = [dict(record) for record in records]
        parallels = self.unpack_parallel_data(results, reconstructed)
        return parallels

    async def get_parallels_count(self,
                                  name: str,
                                  chapter: Optional[str] = None):
        """Count the number of parallels for a given tradition and either a given chapter or a given verse 
        within this chapter.
        """
        query = self.count_parallels_query(name, chapter)
        records = await self.database.fetch_all(query=query)
        return [dict(record) for record in records]

    async def get_collation(self,
                            name: str,
                            chapter: str,
                            verse: str,
                            reconstructed: bool,
                            strip_vowels: bool):
        """Get the collation of the parallels of a tradition for a chapter and a verse.
        """
        collation = Collation()
        records = await self.get_parallels_content(name=name, 
                                                   chapter=chapter, 
                                                   verse=verse,
                                                   reconstructed=reconstructed)
        for manuscript_name, content in records.items():
            if strip_vowels:
                content = strip_hebrew_vowels(content)
            collation.add_plain_witness(manuscript_name, content)
        return collate(collation, output="table", segmentation=False, near_match=True)

    async def get_html_collation(self,
                                 name: str,
                                 chapter: str,
                                 verse: str,
                                 reconstructed: bool,
                                 strip_vowels: bool):
        """Get the collation of the parallels of a tradition for a chapter and a verse as an XML.
        """
        collation = await self.get_collation(name, chapter, verse, reconstructed, strip_vowels)
        return create_table_visualization(collation).get_html_string(formatting=True)
