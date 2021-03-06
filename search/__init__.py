"""
Custom Haystack backend to use the aggregations framework of Elasticsearch.
"""
from haystack.backends import SQ
from haystack.backends.elasticsearch_backend import (
    ElasticsearchSearchBackend, ElasticsearchSearchQuery,
    ElasticsearchSearchEngine,
)
import haystack.query as haystack


class SearchBackend(ElasticsearchSearchBackend):
    def build_search_kwargs(self, query_string, extra=None, *args, **kwargs):
        kwargs = super(SearchBackend, self).build_search_kwargs(
            query_string, *args, **kwargs)
        if extra:
            kwargs.update(extra)
        return kwargs

    def _process_results(self, raw_results, **kwargs):
        results = super(SearchBackend, self)._process_results(
            raw_results, **kwargs)
        if 'aggregations' in raw_results:
            results['aggregations'] = raw_results['aggregations']
        return results


class SearchQuery(ElasticsearchSearchQuery):
    def __init__(self, **kwargs):
        super(SearchQuery, self).__init__(**kwargs)
        self.query_post_filter = None
        self.aggregations = None

    def get_aggregation_results(self):
        if self._aggregation_results is None:
            # TODO handle _raw_query and _more_like_this
            self.run()
        return self._aggregation_results

    def set_post_filter(self, post_filter):
        self.query_post_filter = post_filter

    def set_aggregation_results(self, aggs):
        self.aggregations = aggs

    def build_params(self, *args, **kwargs):
        search_kwargs = super(SearchQuery, self).build_params(*args, **kwargs)

        extra = {}

        if self.query_post_filter:
            post_filter = self.query_post_filter.as_query_string(
                self.build_query_fragment)
            extra['post_filter'] = {
                'query_string': {
                    'query': post_filter,
                },
            }

        if self.aggregations:
            extra['aggs'] = self.aggregations

        if extra:
            search_kwargs['extra'] = extra

        return search_kwargs

    def run(self, *args, **kwargs):
        """
        Builds and executes the query. Returns a list of search results.

        Overrides ElasticsearchSearchQuery.run to also set the
        _aggregation_results attribute.
        """
        final_query = self.build_query()
        search_kwargs = self.build_params(*args, **kwargs)

        results = self.backend.search(final_query, **search_kwargs)
        self._results = results.get('results', [])
        self._hit_count = results.get('hits', 0)
        self._facet_counts = self.post_process_facets(results)
        self._spelling_suggestion = results.get('spelling_suggestion', None)
        self._aggregation_results = results.get('aggregations', None)

    def _clone(self, **kwargs):
        clone = super(SearchQuery, self)._clone(**kwargs)
        clone.query_post_filter = self.query_post_filter
        clone.aggregations = self.aggregations
        return clone


class SearchEngine(ElasticsearchSearchEngine):
    backend = SearchBackend
    query = SearchQuery


class SearchQuerySet(haystack.SearchQuerySet):
    def __init__(self, *args, **kwargs):
        super(SearchQuerySet, self).__init__(*args, **kwargs)
        self._aggregation_results = None

    def post_filter(self, *args, **kwargs):
        """
        Sets the post_filter field in the search request.

        Adds a filter that runs after aggregations.
        """
        clone = self._clone()
        clone.query.set_post_filter(SQ(*args, **kwargs))
        return clone

    def aggregations(self, aggs):
        """
        Sets the aggs field in the search request.

        Specifies aggregations to be computed.
        """
        clone = self._clone()
        clone.query.set_aggregation_results(aggs)
        return clone

    def get_aggregation_results(self):
        """
        Returns the aggregations field in the search results.
        """
        if self._aggregation_results is None:
            self._aggregation_results = self.query.get_aggregation_results()
        return self._aggregation_results
