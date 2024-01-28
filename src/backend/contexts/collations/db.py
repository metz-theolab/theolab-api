"""DB client to fetch textual data from the QWB API.
"""

from backend.tools.sql_client import SQLClient
from collatex import Collation, collate
from collatex.core_classes import create_table_visualization
from .models import FOLLOWED_BY_MAPPER


class ParallelsClient(SQLClient):
    """Manipulate textual data from the QWB API.
    """

    def parallel_query(self,
                       name: str,
                      chapter: str,
                      verse: str):
        """Build the query to retrieve parallels.
        """
        return self.format_query(f"""
                                SELECT ms_B.reading, ms_B.manuscript, ms_B.followed_by
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
                                and  ms_B.position_in_reference=0;"""
                                 )
    
    def unpack_parallel_data(self, records):
        """Unpack the manuscript data into a single string.
        """
        parallels = {}
        for record in records:
            try:
                parallels[record["manuscript"]] += record["reading"] +\
                    FOLLOWED_BY_MAPPER[record["followed_by"]]
            except KeyError:
                parallels[record["manuscript"]] = record["reading"] +\
                    FOLLOWED_BY_MAPPER[record["followed_by"]]
        return parallels
    
    async def get_parallels(self,
                      name: str,
                      chapter: str,
                      verse: str):
        """Get all the parallels as a dictionary of manuscript name and text.
        """
        records = await self.database.fetch_all(query=self.parallel_query(name, chapter, verse))
        return list(set([dict(record)["manuscript"] for record in records]))

    async def get_parallels_content(self,
                      name: str,
                      chapter: str,
                      verse: str):
        """Get all the parallels as a list of text for a tradition, a chapter and a verse.
        """
        records = await self.database.fetch_all(query=self.parallel_query(name, chapter, verse))
        results = [dict(record) for record in records]
        return self.unpack_parallel_data(results)
        
    async def get_html_collation(self,
                            name: str,
                            chapter: str,
                            verse: str):
        """Get the collation of the parallels of a tradition for a chapter and a verse as an XML.
        """
        collation = Collation()
        records = await self.get_parallels_content(name, chapter, verse)
        for manuscript_name, content in records.items():
            collation.add_plain_witness(manuscript_name, content)
        return create_table_visualization(collate(collation, output="table", segmentation=True)).get_html_string(formatting=True)
        
