# This file is part of Tryton.  The COPYRIGHT file at the top level of this
# repository contains the full copyright notices and license terms.
from decimal import Decimal
from dateutil import relativedelta

from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['Asset']

class Asset():
    __metaclass__ = PoolMeta
    __name__ = 'account.asset'

    rate = fields.Numeric('Rate',
        digits=(14, 10),
        states={
            'readonly': (Eval('lines', [0]) | (Eval('state') != 'draft')),
            'invisible': (Eval('depreciation_method') != 'declining_balance'),
            'required': (Eval('depreciation_method') == 'declining_balance'),
            },
        depends=['state', 'depreciation_method'])
    half_year_rule = fields.Boolean('Half Year Rule',
        states={
            'readonly': (Eval('lines', [0]) | (Eval('state') != 'draft')),
            'invisible': (Eval('depreciation_method') != 'declining_balance'),
            },
        depends=['state', 'depreciation_method'])

    @classmethod
    def __setup__(cls):
        super(Asset, cls).__setup__()
        cls.depreciation_method.selection.append(('declining_balance', 'Declining Balance'))

    def compute_depreciation(self, date, dates):
        """
        Returns the depreciation amount for an asset on a certain date.
        """
        # calculate remaining amount to depreciate.
        amount = (self.value - self.get_depreciated_amount() -
                  self.residual_value)
        if self.depreciation_method == 'linear':
            super(Asset, cls).compute_depreciation(self, date, dates)
        elif self.depreciation_method == 'declining_balance':
            # V = P * (1 - R) ** N
            #     V is the depreciated value after N periods
            #     P is value to depreciate
            #     R is rate of depreciation at each period
            start_date = max([self.start_date
                    - relativedelta.relativedelta(days=1)]
                + [l.date for l in self.lines])
            # Calculate number of periods in depreciation range.
            delta = relativedelta.relativedelta(date, start_date)
            if self.frequency == 'monthly':
                period = delta.months + 12 * delta.years
                if delta.days > 0:
                    period += 1
            elif self.frequency == 'yearly':
                period = delta.years
                if delta.months > 0:
                    period += 1
            if self.get_depreciated_amount() > 0:
                # Asset has some depreciation posted.
                # Half Year Rule irrelevant here.
                #
                print "Depreciating unposted remainder."
            else:
                # Asset has not posted depreciation yet.
                balance = self.value
                for n in range(0, period):
                    depreciation = (balance - self.residual_value) * self.rate
                    if n == 0 and self.half_year_rule:
                        depreciation *= Decimal(0.5)
                    balance -= depreciation
            return self.company.currency.round(depreciation)
