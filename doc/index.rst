Account Asset (Declining Balance Depreciation) Module
#####################################################

The account_asset_db module extends the account_asset module by adding the
declining balance depreciation method. of fixed assets.

Asset
*****

- Depreciation Method:
  - Declining Balance with Half Year Rule option.

The declining balance depreciation method decreases the undepreciated value of
a fixed asset every period by a fixed rate. The current value, V, of a fixed
asset after N periods with a depreciation rate or R is calculated as:

  V = P (1 - R) ** N

The Half Year Rule option allows for halving the first year's depreciation
amount.
