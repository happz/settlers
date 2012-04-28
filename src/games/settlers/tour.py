import tournament

class TournamentRules(tournament.TournamentRules):
  def __init__(self, flags):
    super(TournamentRules, self).__init__(flags)

    self.floating_desert = flags.floating_desert
