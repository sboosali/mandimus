import mdlog
log = mdlog.getLogger(__name__)

from MappingRule import MappingRule

class SeriesMappingRule(MappingRule):
    allowCombining = True
    serializedType = "SeriesMappingRule"

def combineSeriesMappingRules(series):
    class MergedSeries(SeriesMappingRule):
        mapping = {}
        extras = []
        defaults = {}
        parts = []
        allowCombining = False
        isMergedSeries = True
        
    name = []

    for a in series:
        commonKeys = set(MergedSeries.mapping.keys()) & set(a.mapping.keys()) 
        if commonKeys:
            log.info("MergedSeries and %s have mapping keys in common, skipping. Keys: %s" % (type(a).__name__, commonKeys))
            continue
        MergedSeries.mapping.update(a.mapping.items())
        
        # love me some n^2 on small inputs
        for i in a.extras:
            for j in MergedSeries.extras:
                if i.name == j.name and i != j:
                    log.info("MergedSeries and %s disagree on extras (%s) (%s)" % (type(a).__name__, i, j))
        MergedSeries.extras += a.extras
        
        for i in a.defaults:
            if i in MergedSeries.defaults:
                if a.defaults[i] != MergedSeries.defaults[i]:
                    log.info("MergedSeries and %s disagree on defaults (%s) (%s)" % (type(a).__name__, a.defaults[i], MergedSeries.defaults[i]))
        MergedSeries.defaults.update(a.defaults.items())

        MergedSeries.parts.append(a)

    MergedSeries.parts.sort(key=lambda x: type(x).__name__)
    MergedSeries.__name__ = ','.join([type(x).__name__ for x in MergedSeries.parts])

    # print MergedSeries.mapping
    # print MergedSeries.extras
    # print MergedSeries.defaults

    return MergedSeries
