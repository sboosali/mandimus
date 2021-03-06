import mdlog
log = mdlog.getLogger(__name__)


from dragonfly import CompoundRule, MappingRule, RuleRef, Repetition

# taken from dictation-toolbox
# https://github.com/dictation-toolbox/dragonfly-scripts/blob/f639abf167fdd59ca9ad8039f4ff582deeda34e0/dynamics/subversion_grammar.py

class SeriesMappingRule(CompoundRule):
    """Just like a mapping rule except it lets you repeat commands."""
    
    def __init__(self, name=None, mapping=None, extras=None, defaults=None, exported=True):
        mapping_rule = MappingRule(mapping=mapping, extras=extras,
                                   defaults=defaults, exported=False,
                                   name=name + "Mapping")
        single = RuleRef(rule=mapping_rule)
        series = Repetition(single, min=1, max=5, name="series")

        compound_spec = "<series>"
        compound_extras = [series]
        CompoundRule.__init__(self, name=name, spec=compound_spec,
                              extras=compound_extras, exported=exported)

    def _process_recognition(self, node, extras):  # @UnusedVariable
        series = extras["series"]
        for action in series:
            action.execute()

### DRAGONSHARE RSYNC
