#import "Styles.m"
int main(int argc,char **argv){@autoreleasepool{
 if(argc!=4)return 2;
 NSError *e=nil;NSDictionary *r=XDStylesPerform(@{@"operation":@"styles-decode-reverse",@"input_path":@(argv[1]),@"output_path":@(argv[2]),@"max_edge":@(atoi(argv[3])),@"supported_metadata_versions":@[@8,@9,@15,@16]},&e);
 if(!r){fprintf(stderr,"%s\n",e.description.UTF8String);return 3;}
 [[NSJSONSerialization dataWithJSONObject:VMJSONSafe(r) options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:[@(argv[2]) stringByAppendingPathComponent:@"reverse.json"] atomically:YES];
 return 0;
}}
