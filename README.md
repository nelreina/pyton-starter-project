# Project srv-datawarehouse 

Service to load the TCB datawarehouse once a day

### Configuration 

create the following file in the root directory: .env.dw

Place the following content
```sh
STREAM=<stream name>

REDIS_HOST=redis
#REDIS_USER=
#REDIS_PW=

CONN_TCB_DATA= <connection to tcb data database> 
CONN_DODW=<connection to Digital Ocean Databse >

SCHEDULE_TIME_DW=<Scheduled Run time >

DW_TABLE_BOOKING_METHOD=booking_method_clicks
DW_TABLE_TCB=vet_tcb_data_warehouse_new

# API for getting master data and cache in Redis e.g. airlines, stays etc ... 
DECLARATION_API=https://tourismtax.bonairegov.com/api-declarations/
```
