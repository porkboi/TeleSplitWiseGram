# TeleSplitWiseGram
This is a Bill Splitting Telegram Bot

## Setup
Insert Telegram Bot token in fakeDb.json
Add the bot to your group

## How it works
Use commands /start to bring up the instructions

/newtrip - starts a new trip
/sum - used to declare owing someone money
/split - used to charge a group of people money equally
/receipt - brings up the receipt
/endtrip - wipes your data from the database

## How the code works
This uses PyTelegramBot API for most of its functions albeit some custom algorithms.

The storage for the bot lies in indexing n^2 integers - implicitly assining a serial number to each user, allowing the bot to keep track of money flows. Iterations are done using modulo n as well.

Receipt simplification lies in identifying these modulo conjugates, ie. (1*n) + 3 and (3*n) + 1 are modulo conjugates, these serve to be the pair of indexes where money owed is compared and the delta is computed.
