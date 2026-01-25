# Services

There are a few services available within this integration, which are detailed here.

# Holidays

## smol.start_holiday_mode

Puts a Smol account into holiday mode.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the holiday sensor (i.e. `binary_sensor.smol_{{ACCOUNT_NAME}}_is_on_holiday`) that represents the account to put into holiday mode.                                                   |
| `data.end_date_time`      | `no`    | The datetime for when your holiday should end. |

## smol.end_holiday_mode

Takes a Smol account out of holiday mode

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the holiday sensor (i.e. `binary_sensor.smol_{{ACCOUNT_NAME}}_is_on_holiday`) that represents the account to put into holiday mode.                                                   |

## smol.change_next_charge_date

Changes the next charge date for a Smol subscription

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the holiday sensor (i.e. `sensor.smol_{{ACCOUNT_NAME}}_{{PRODUCT_ID}}_subscription_next_charge`) that represents the account to put into holiday mode. 
| `data.next_charge_date`      | `no`    | The next charge date to change the subscription to. |
