from MappingRule import MappingRule

class SeriesMappingRule(MappingRule):
    allowCombining = True
    serializedType = "SeriesMappingRule"

def combineSeriesMappingRules(series):
    class MergedSeries(SeriesMappingRule):
        mapping = {}
        extras = []
        defaults = {}
        
    name = []

    for a in series:
        commonKeys = set(MergedSeries.mapping.keys()) & set(a.mapping.keys()) 
        if commonKeys:
            print "MergedSeries and %s have mapping keys in common, skipping. Keys: %s" % (type(a).__name__, commonKeys)
            continue
        MergedSeries.mapping.update(a.mapping.items())
        
        # love me some n^2 on small inputs
        for i in a.extras:
            for j in MergedSeries.extras:
                if i.name == j.name and i != j:
                    print "MergedSeries and %s disagree on extras (%s) (%s)" % (type(a).__name__, i, j)
        MergedSeries.extras += a.extras
        
        for i in a.defaults:
            if i in MergedSeries.defaults:
                if a.defaults[i] != MergedSeries.defaults[i]:
                    print "MergedSeries and %s disagree on defaults (%s) (%s)" % (type(a).__name__, a.defaults[i], MergedSeries.defaults[i])
        MergedSeries.defaults.update(a.defaults.items())

        name.append(type(a).__name__)

    name.sort()
    MergedSeries.__name__ = ''.join(name)

    # print MergedSeries.mapping
    # print MergedSeries.extras
    # print MergedSeries.defaults

    return MergedSeries
