export LANG=en_US.utf8
PLUGIN_HOME=$1
epg2xml run --config %PLUGIN_HOME%/file/epg2xml.json --channelfile %PLUGIN_HOME%/file/Channel.json --xmlfile %PLUGIN_HOME%/file/xmltv.xml