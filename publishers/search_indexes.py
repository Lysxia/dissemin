from .models import Publisher
from haystack import indexes


class PublisherIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    num_papers = indexes.IntegerField(model_attr='stats__num_tot', default=0)
    oa_status = indexes.CharField(model_attr='oa_status')
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Publisher
