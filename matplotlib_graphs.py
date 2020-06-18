# Summary of matplotlib graphs used in the study.

# MEASURED: LINE PLOT DG1, DG2, STOP TIMER, DG3
plt.subplot(4, 1, 1)
df['DG1'].plot()
plt.ylabel('Load [%]')
plt.title('DG1 LOAD, DG2 LOAD, STOP TIME COUNTER AND DG3 LOAD')
plt.subplot(4, 1, 2)
df['DG5'].plot()
plt.ylabel('Load [%]')
plt.subplot(4, 1, 3)
plt.plot([item[-1] for item in simulate_running])
plt.ylabel('Counter')
plt.subplot(4, 1, 4)
df['DG4'].plot()
plt.ylabel('Load [%]')
plt.show()




#  LINE PLOTS: MEASURED TOTAL POWER, ESTIMATED STOP TIME, ESTIMATED CHANGE IN NUMBER OF ENGINES
plt.subplot(3, 1, 1)
plt.plot(df['TOT_POW'])
plt.title('TOTAL POWER IN kW')
plt.subplot(3, 1, 2)
plt.plot([item[-1] for item in simulate_running])
plt.title('MODEL: STOP TIME')
plt.subplot(3, 1, 3)
plt.plot([item[2] for item in simulate_running])
plt.title('MODEL: CHANGE IN NUMBER OF ENGINES')
plt.show()




#  START TIME LINE PLOTS
plt.subplot(2, 1, 1)
plt.plot(df['ST'])
plt.title('MEASURED: START TIME')
plt.subplot(2, 1, 2)
plt.plot([item[-1] for item in simulate_running])
plt.title('MODEL: START TIME')
plt.show()




#  DG1 HISTOGRAM
data=[[item[3][0,0] for item in simulate_running]]
arr=plt.hist(data, bins=bins, log=True, range=[-1,150])
for i in range(bins):
    plt.text(arr[1][i],arr[0][i],str(arr[0][i]))
plt.title('MODEL: DG1 LOAD')
plt.show()




# LINE SUBPLOTS OF DG1 MEASURED AND DG1 ESTIMATED LOAD
plt.subplot(2, 1, 1)
plt.plot(df['DG1'])
plt.title('MEASURED: DG1 LOAD')
plt.subplot(2, 1, 2)
plt.plot([item[3][0,0] for item in simulate_running])
plt.title('MODEL: DG1 LOAD')
plt.show()




#  LINE SUBPLOTS OF MEASURED AND ESTIMATED CHANGE IN NUMBER OF ENGINES
plt.subplot(2, 1, 1)
plt.plot(df['ENGINES'])
plt.title('MEASURED: CALCULATION OF REQUIRED ENGINES')
plt.subplot(2, 1, 2)
plt.plot([item[2] for item in simulate_running])
plt.title('MODEL: CHANGE IN NUMBER OF ENGINES')
plt.show()




# HISTOGRAM DG1 MEASURED AND ESTIMATED
plt.subplot(2, 1, 1)
arr=plt.hist(df['DG1'], bins=bins, log=True, range=[-1,160])
for i in range(bins):
    plt.text(arr[1][i],arr[0][i],str(arr[0][i]))
plt.title('MEASURED: DG1 LOAD')
plt.subplot(2, 1, 2)
data=[[item[3][0,0] for item in simulate_running]]
arr=plt.hist(data, bins=bins, log=True, range=[-1,160])
for i in range(bins):
    plt.text(arr[1][i],arr[0][i],str(arr[0][i]))
plt.title('ESTIMATED: DG1 LOAD')
plt.show()




# MEAN LOAD PER ENGINE MEASURED AND ESTIMATED
plt.subplot(2, 1, 1)
df['MEAN POWER'] = df['TOT_POW'] / df['ENGINES'] / 1830 * 100
arr = plt.hist(df['MEAN POWER'], bins=bins, log=True, range=[-1, 160])
for i in range(bins):
    plt.text(arr[1][i], arr[0][i], str(arr[0][i]))
plt.title('MEASURED: MEAN LOAD PER ENGINE')
plt.subplot(2, 1, 2)
data = [[item[4] for item in simulate_running]]
arr = plt.hist(data, bins=bins, log=True, range=[-1, 160])
for i in range(bins):
    plt.text(arr[1][i], arr[0][i], str(arr[0][i]))
plt.title('ESTIMATED: MEAN LOAD PER ENGINE')
plt.show()




# HISTOGRAM 5X ENGINES ESTIMATED
for i in range(1, 6):
    plt.subplot(5, 1, i)
    data = [[item[3][0, i-1] for item in simulate_running]]
    arr=plt.hist(data, bins=bins, log=True, range=[-1,130])
    for i in range(bins):
        plt.text(arr[1][i], arr[0][i], str(arr[0][i]))
    plt.xlabel('Load [%]')
plt.title('MODEL: ALL DG HISTOGRAMS')
plt.show()



# MEASURED: LINE PLOT, ALL FIVE ENGINES
plt.subplot(3, 1, 1)
df['DG1'].plot()
plt.ylabel('Load [%]')
plt.title('MEASURED: DG1, DG2 AND DG3 LOAD')
plt.subplot(3, 1, 2)
df['DG5'].plot()
plt.ylabel('Load [%]')
plt.subplot(3, 1, 3)
df['DG4'].plot()
plt.ylabel('Load [%]')
plt.show()