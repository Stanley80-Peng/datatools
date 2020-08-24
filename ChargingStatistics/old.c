#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

#define FILEPATH "planner"
#define MAX_LEN_FILE_NAME 100
#define MAX_LEN_REASON 22



typedef struct fail{
    char fail_time[MAX_LEN_REASON];
    char main_reason[MAX_LEN_REASON], stuck_phase[MAX_LEN_REASON];
    int try_times;
    struct fail * next_reason;//init into NULL
} fail;

typedef struct file{
    char file_name[MAX_LEN_FILE_NAME];
    struct file * next_file;//init into NULL
} file;

typedef struct day_stat{
    int begin, over, success, fail, retry;
    fail ** fail_list;//init * into 0 and the first *() to NULL
} day_stat;

char path_name[MAX_LEN_FILE_NAME], temp_line_data[BUFSIZ], error_time[20];//missing original *reason
int min_date, now_day;//inited
DIR * dir;//inited
struct dirent *entry;//no need to init
FILE * output_file;//inited
file ** file_list;//inited
day_stat total_data;//no need to init
day_stat * current_day_stat;

void init(void);
int open_dir(void);
int create_file_list(void);
void store_file_name(char *);
void get_data(void);
void get_data_from_single_file(char *);
void output_day_data(void);
int date_to_num(const char *);
void add_and_zero(day_stat *);
void output_total(void);

int main(void){
    init();//init global variables
    if(open_dir()) return -1;
    if(create_file_list()) return 1;
    output_file = fopen("Charge_statistics.csv", "w");
    fprintf(output_file, "date,begin,over,success,fail,retry,fail,time,reason,stuck phase,try times\n");
    get_data();
    output_total();
    return 0;
}

void init(void){
    dir = NULL;
    output_file = NULL;
    min_date = now_day = -1;
    file_list = (file **)malloc(sizeof(file *));
    *file_list = (file *)malloc(sizeof(file));
    memset(*file_list, 0, sizeof(file));
    current_day_stat = (day_stat *) malloc(sizeof(day_stat));
    memset(current_day_stat, 0, sizeof(day_stat));
    current_day_stat->fail_list = (fail **)malloc(sizeof(fail *));
    memset(current_day_stat->fail_list, 0, sizeof(fail *));
    *(current_day_stat->fail_list) = (fail *)malloc(sizeof(fail));
    (*(current_day_stat->fail_list))->next_reason = NULL;
}

int open_dir(void){
    if((dir = opendir(FILEPATH)) == NULL){
        printf("Fail to open dir \"%s\"", FILEPATH);
        return 1;
    }
    else{
        printf("Dir \"%s\" opened\n", FILEPATH);
        return 0;
    }
}

int create_file_list(void){
    int file_count=0, file_abort=0;
    while((entry=readdir(dir))){
        if(strstr(entry->d_name, "planner")&&strstr(entry->d_name, "INFO")&&
           strstr(entry->d_name, "airobot")){
            printf("Accept file \"%s\"\n", entry->d_name);
            file_count++;
            store_file_name(entry->d_name);
        }
        else{
            printf("Abort file \"%s\"\n", entry->d_name);
            if(entry->d_reclen>=3) file_abort++;
        }
    }
    if(!file_count){
        if(file_abort) printf("Can't find any planner_info log in dir \"%s\"\n", FILEPATH);
        else printf("Empty dir \"%s\" please check!\n", FILEPATH);
        return 1;
    }
    else return 0;
}

void store_file_name(char * current_file_name){
    file * process_file = (file *)malloc(sizeof(file));
    process_file->next_file = NULL;
    strcpy(process_file->file_name, current_file_name);
    if((*file_list)->next_file == NULL){
        (*file_list)->next_file = process_file;
    }
    else{
        file * iter = *file_list;
        while(strcmp(current_file_name, iter->next_file->file_name) > 0 && (iter->next_file)->next_file != NULL)
            iter = (file *) iter->next_file;
        if(strcmp(current_file_name, iter->next_file->file_name) < 0){
            process_file->next_file = iter->next_file;
            iter->next_file = process_file;
        }
        else {
            process_file->next_file = iter->next_file->next_file;
            iter->next_file->next_file = process_file;
        }
    }
}

void get_data(void){
    file * iter = (*file_list)->next_file;
    while(iter != NULL){
        get_data_from_single_file(iter->file_name);
        iter = iter->next_file;
    }
    output_day_data();
    add_and_zero(current_day_stat);
}

void get_data_from_single_file(char * current_file_name){
    int retry_flag;
    sprintf(path_name, "%s/%s", FILEPATH, current_file_name);
    FILE * input_file = fopen(path_name, "r");
    printf("File opened \"%s\"\n", current_file_name);
    while(fgets(temp_line_data, BUFSIZ - 1, input_file)){
        if(temp_line_data[0] != 'I') continue;
        if(min_date == -1) min_date = date_to_num(temp_line_data+1);
        if (now_day == -1) {
            now_day = date_to_num(temp_line_data + 1);
        }
        else if(now_day != date_to_num(temp_line_data + 1)){
            output_day_data();
            add_and_zero(current_day_stat);
            now_day = date_to_num(temp_line_data + 1);
        }
        if (strstr(temp_line_data, "<Charge>[ BEGIN ]") != NULL){
            retry_flag = 0;
            current_day_stat->begin++;
            while(fgets(temp_line_data, BUFSIZ-1, input_file)){
                if(strstr(temp_line_data, "<Charge>[ OVER ]") != NULL){
                    current_day_stat->over++;
                    break;
                }
                if(strstr(temp_line_data, "<Charge>[ SUCCESS ]") != NULL)  current_day_stat->success++;
                if(strstr(temp_line_data, "adjust") || strstr(temp_line_data, "phase 5")) retry_flag = 1;
                if(strstr(temp_line_data, "<Charge>[ FAIL ]") != NULL){
                    current_day_stat->fail++;
                    fail * new_fail = (fail *)malloc(sizeof(fail));
                    new_fail->next_reason = NULL;
                    retry_flag = 0;
                    strncpy(new_fail->stuck_phase, strrchr(temp_line_data,'['),strrchr(temp_line_data, ']')-strrchr(temp_line_data,'[')+1);
                    new_fail->stuck_phase[MAX_LEN_REASON-1]= 0;
                    fgets(temp_line_data, BUFSIZ-1, input_file);//
                    sscanf(temp_line_data+6, "%s", new_fail->fail_time);
                    new_fail->try_times = atoi(strrchr(temp_line_data, 'R')+22);
                    strncpy(new_fail->main_reason, strrchr(temp_line_data,'['),strrchr(temp_line_data, ']')-strrchr(temp_line_data,'[')+1);
                    if((*(current_day_stat->fail_list))->next_reason == NULL)
                        (*(current_day_stat->fail_list))->next_reason = new_fail;
                    else{
                        fail * iter_fail = (*(current_day_stat->fail_list))->next_reason;
                        while(iter_fail->next_reason != NULL) iter_fail = iter_fail->next_reason;
                        iter_fail->next_reason = new_fail;
                    }
                }
            }
            if(retry_flag) current_day_stat->retry++;
        }
    }
}

int date_to_num(const char * date_str){
    int date_num, i;//ASCII char to digit should -48
    date_num = 1000*(*date_str-48)+100*(*(date_str+1)-48)
            +10*(*(date_str+2)-48)+(*(date_str+3)-48);
    return date_num;
}

void output_day_data(void){
    int fail_time;
    fprintf(output_file, "%d,%d,%d,%d,%d,%d\n", now_day, current_day_stat->begin, current_day_stat->over,
            current_day_stat->success, current_day_stat->fail, current_day_stat->retry);
    fail * fail_iter = (*(current_day_stat->fail_list))->next_reason;
    fail_time = 0;
    while(fail_iter != NULL){
        fprintf(output_file, " ,,,,,,%d,%s,%s,%s,%d\n", fail_time+1, fail_iter->fail_time, fail_iter->main_reason,
                fail_iter->stuck_phase, fail_iter->try_times);
        fail_iter = fail_iter->next_reason;
        fail_time++;
    }
    fputc(10, output_file);
    printf("Print day %d over\n", now_day);
}

void add_and_zero(day_stat * zero_day_stat){
    total_data.begin += zero_day_stat->begin;
    total_data.over += zero_day_stat->over;
    total_data.success += zero_day_stat->success;
    total_data.fail += zero_day_stat->fail;
    zero_day_stat->begin = zero_day_stat->over = zero_day_stat->success =
            zero_day_stat->fail = zero_day_stat->retry = 0;
    (*(zero_day_stat->fail_list))->next_reason = NULL;
}

void output_total(void){
    fprintf(output_file, "total,from,%d,to,%d\n", min_date, now_day);
    fprintf(output_file, " ,begin,over,success,fail,retry\n ,%d,%d,%d,%d,%d\n", total_data.begin, total_data.over,
            total_data.success, total_data.fail, total_data.retry);
}
