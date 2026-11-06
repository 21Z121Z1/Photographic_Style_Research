#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreMedia/CoreMedia.h>

int main(int argc,char **argv){@autoreleasepool{
    if(argc!=2)return 2;
    AVAsset *a=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:@(argv[1])] options:nil];
    for(AVMetadataItem *i in a.metadata)if([i.identifier containsString:@"style"])
        NSLog(@"ASSET %@ = %@",i.identifier,i.value);
    for(AVAssetTrack *t in a.tracks){
        if(![t.mediaType isEqualToString:AVMediaTypeMetadata])continue;
        NSError *error=nil;AVAssetReader *r=[[AVAssetReader alloc]initWithAsset:a error:&error];
        AVAssetReaderTrackOutput *o=[[AVAssetReaderTrackOutput alloc]initWithTrack:t outputSettings:nil];
        [r addOutput:o];AVAssetReaderOutputMetadataAdaptor *ad=[[AVAssetReaderOutputMetadataAdaptor alloc]initWithAssetReaderTrackOutput:o];
        if(![r startReading]){NSLog(@"%@",r.error);return 1;}
        AVTimedMetadataGroup *g;NSMutableDictionary *counts=[NSMutableDictionary new];
        while((g=[ad nextTimedMetadataGroup]))for(AVMetadataItem *i in g.items){
            NSString *name=i.identifier?:@"unknown";NSUInteger count=[counts[name]unsignedIntegerValue];counts[name]=@(count+1);
            if(count)continue;
            if([i.value isKindOfClass:NSData.class]){
                NSDictionary *p=[NSPropertyListSerialization propertyListWithData:(NSData*)i.value options:0 format:NULL error:NULL];
                NSMutableDictionary *summary=[NSMutableDictionary new];
                for(id key in p){id v=p[key];summary[[key description]]=[v isKindOfClass:NSData.class]?@{ @"bytes":@([v length])}:v;}
                NSLog(@"META %@ PTS %.9f = %@",name,CMTimeGetSeconds(g.timeRange.start),summary);
            }else NSLog(@"META %@ = %@",name,i.value);
        }
        NSLog(@"TRACK %d COUNTS %@",t.trackID,counts);
    }
    return 0;
}}
