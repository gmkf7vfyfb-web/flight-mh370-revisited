=======================================================================================
  
  Antarctic blue whales in the southern Indian Ocean: a multi-year and multi-site 
  database of Z-call detections.

=======================================================================================

 Reference: Leroy, E., Samaran, F., Bonnel, J. & Royer, J.-Y., 2016a. Seasonal and diel
 vocalization patterns of Antarctic blue whale (Balaenoptera musculus intermedia) in the
 Southern Indian Ocean: a multi-year and multi-site study, Plos One, in press (Sept.2016).

File description:

-"detections_[station]_[year].csv" 
These files provide the results of Z-calls automated detection for each station (except RAMA, where no Z-call was present) and each available year (see Fig 2). 
Each row is a detection, with associated information : Columns 1 to 7 are respectively the year, julian day (i.e. number of days since the 1st of January of the given year), month, corresponding week, hours, minutes and seconds of the detection. Column 8 indicates the SNR (Signal to Noise Ratio) of the detection, and column 9 indicates the data source file where the Z-call was detected. 

-“ambientnoise_[station].csv" 
These files provide the ambient noise level (in dB re 1µPa²/Hz) in the 40-60Hz bandwidth, estimated over 300s-windows in 0.0018 Hz-bins, averaged per julian day for each year. 
NaN indicate unavailable measurements due to data gaps. Ambient noise level measurements are available for all stations (RAMA, MAD, NEAMS, SSEIR, NCRO, SWAMS, WKER).

-"Chorus_to_Noise_Ratio_[station].csv" 
These files provide the level of CNR (Chorus to Noise-without-chorus Ratio) averaged per julian day and given for each year of data. 
To estimate this CNR, the chorus level is calculated in a frequency band set to 25.5 - 26.8 Hz for 2010 and 2011 datasets; 25.5 - 26.7 Hz for 2012 data; 25.5 - 26.5 Hz for 2013 and 2014; and 25.5 - 26.1 Hz for 2015. 
This chorus level (in dB re 1 μPa2/Hz) is then subtracted from the noise level in the 30-33 Hz frequency band, and averaged per julian day. 
CNR measurements are available for each station except RAMA. 
NaN indicate unavailable measurements due to data gaps.

