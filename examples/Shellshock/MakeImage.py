import json
import numpy as np
import matplotlib.pyplot as plt

def process_data(version):
    print "Opening:\t"+version
    f = open(version+'.log','r')
    D = json.load(f)

    

    image = []
    i=0
    print "found %d patches"% len(D)
    for patches in D:
        cves=[]
        for cve in patches[0]:
            if version=='3.2' and i>=12 and i<=25:
                cves.append(True)
            else:
                cves.append(cve['vuln'])
        image.append(cves)
        i+=1
    return image



images = {}
versions = ['3.0','3.1','3.2','4.0','4.1','4.2','4.3']
for version in versions:
    images[version]=process_data(version)



N = 5
ind = np.arange(N)
f, axarr = plt.subplots(1,len(versions), sharey=True)
for j in xrange(0,len(images)):
    version = versions[j]
    image = images[version]
    p = axarr[j]
    print "Plotting %s:\t%d"%(version,len(image))
    i = 0
    for i in xrange(0,len(image)):
        patch = image[i]
        b1 = p.bar(ind,map(lambda x: 1 if x else 0, patch[0:-2]), 1, color='#880000',bottom=i)
        b2 = p.bar(ind,map(lambda x: 0 if x else 1, patch[0:-2]), 1, color='#77ff77',bottom=i,hatch="X")
    
    plt.sca(p)
    plt.xticks(ind+1./2., ('2014-6271', '2014-6277', '2014-6278', '2014-7169', '2014-7186') ,rotation='vertical')
    p.set_title("Bash v"+version)
    #plt.yticks(np.arange(0,60,1))

#f.subplots_adjust(wspace=1)
#plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

plt.legend([b1[0],b2[0]],['Vulnerable','Invulnerable'])
plt.sca(axarr[0])
plt.ylabel('Patch')
fig = plt.gcf()
fig.set_size_inches(10,11)
f = open('ShellshockData.png','w')
plt.savefig(f,dpi=100,bbox_inches='tight')
f.close()
