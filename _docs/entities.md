# Entities

The following entities are available with each configured account

## Is On Holiday

`binary_sensor.smol_{{ACCOUNT_NAME}}_is_on_holiday`

Binary sensor to determine if your account is currently in holiday mode

## Holiday End Date

`sensor.smol_{{ACCOUNT_NAME}}_holiday_end_date`

Sensor to determine the end date of your holiday for your account

## Subscription Quantity

`sensor.smol_{{ACCOUNT_NAME}}_{{PRODUCT_ID}}_subscription_quantity`

Sensor indicating the quantity of items that are present in each delivery of your subscription. For example, this might return 30 if you are subscribed to 30 dishwasher tablets.

## Subscription Next Charge

`sensor.smol_{{ACCOUNT_NAME}}_{{PRODUCT_ID}}_subscription_next_charge`

Sensor indicating the next time the subscription will be charged. When this changes and you're not in holiday mode, it's a good indication that a subscription has been sent.

This can be changed using the [change next charge date service](./services.md#smolchange_next_charge_date).