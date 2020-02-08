int NbProcs = ...;
int NbTasks = ...;
int Cycles = ...;
int Max = 100000;
int maxValue = 100000;
int maxTime = 100000;


int xN = ...;
int yN = ...;

range Procs = 1..NbProcs;
range Tasks = 1..NbTasks;
range Cycle = 1..Cycles;
range maxValueRange = 0..maxValue;
range maxTimeRange = 0..maxTime;
int Time[Procs][Tasks] = ...;
int comm[Tasks][Tasks] = ...;
int Dep[Tasks][Tasks] = ...;
int shared[Procs][Procs][Procs][Procs]=...;


/*MPPA-256 NOC*/
int link=7;
int rout=8;
////////////////
int delay = 1;
int elink= 1;
int erout = 4;

/* the speed of processors*/
int Freq[Procs]=...;

/*power consumption*/
int dPk[Procs]=...;
int sPk[Procs]=...;

/* the maximal load of every processors*/
int maxP =3;

/* the location of processors*/
int xP[Procs]=...;
int yP[Procs]=...;


/**------------------varaibles -------------------------*/
/* mappig between core and tile, added in 25, May, 2017*/
dvar boolean c2t[Procs][Procs];
dvar boolean a2c[Tasks][Procs];


/*mapping relation between tasks and processors*/
dvar boolean Map[Tasks][Procs];
/*load of every processor*/
dvar int Load[Procs] in maxTimeRange;

/*whehter communicaiton exists between two tasks*/
dvar boolean o[Tasks][Tasks];

/*whether the two tasks are mapped to the same processor*/
dvar boolean b[Tasks][Tasks];

/*the exact mapping of tasks on a processor*/
dvar boolean bp[Procs][Tasks][Tasks];

/*the execution sequence between tasks on the same processor*/
dvar boolean q[Procs][Tasks][Tasks];
dvar int dis[Tasks][Tasks] in 0..xN+yN;

/*the execution time of a task on different cycles */
dvar int tao[Cycle][Tasks] in maxTimeRange;
dvar int fin[Cycle][Tasks] in maxTimeRange;

/*the point of sending actions*/
dvar int se[Cycle][Tasks][Tasks] in maxTimeRange;
dvar int fe[Cycle][Tasks][Tasks] in maxTimeRange;

/*whether conflict exists between two communication*/
dvar boolean conflict[Tasks][Tasks][Tasks][Tasks];

/*the execution time for the last task in the last cycle*/
dvar int MP in maxTimeRange;

/*energy consumption*/
dvar int En in maxValueRange;
dvar int Ed in maxValueRange;
dvar int Es[Procs] in maxValueRange;
dvar int Ec[Tasks][Tasks] in maxValueRange;


/*=====================================================================*/
/* constraints on goals */
 subject to {
	/*bound*/

	forall(k in Procs){
        Load[k] >= 0;
        Load[k] <= maxValue;
        Es[k] >= 0;
        Es[k] <= maxValue;
    }
	forall(i,j in Tasks){
		Ec[i][j] >= 0;
		Ec[i][j] <= maxValue;
	}
    /*for objective optimization*/
    forall(k in Procs){
        Load[k] == sum(i in Tasks)(Time[k][i]*a2c[i][k]);
    }

    Ed == sum(k in Procs)(dPk[k]*Load[k])*Cycles;

    forall(k in Procs){
        (sum(i in Tasks)a2c[i][k]==0)+(Es[k] == sPk[k]*(MP-Load[k]*Cycles))>=1;
        (sum(i in Tasks)a2c[i][k]>=1)+(Es[k] == 0)>=1;
    }
    forall(i in Tasks)
        Ec[i][i]==0;
    forall(i,j in Tasks:i!=j){
        (o[i][j]>=1)+(Ec[i][j]==0)>=1;
        (o[i][j]==0)+(Ec[i][j]== comm[i][j]*(erout*(dis[i][j]+1)+elink*dis[i][j])*Cycles)>=1;
    }

    En == Ed+ sum(k in Procs)Es[k]+sum(i,j in Tasks)Ec[i][j];


/*=====================================================================*/
/*           static constraints */
    /*every task can only be mapped to one processor*/
    forall(i in Tasks)
      ct1:
      sum(k in Procs)
        Map[i][k]==1;

    /*every processor has at least one task*/
    forall(k in Procs)
      ct2:
     {
      sum(i in Tasks)Map[i][k]<=maxP;
     }

    /*whether tasks are on the same processor*/
    forall(i in Tasks)
        ct50:
        b[i][i]==0;
    forall(i,j in Tasks: i!=j)
        ct51:
        b[i][j]==1-(sum(k in Procs)(abs(Map[i][k]-Map[j][k])))/2;

    /*tasks are on which processor*/
    forall(i,j in Tasks, k in Procs: i!=j)
        ct60:
        bp[k][i][j] <= (Map[i][k] + Map[j][k])/2;

    forall(i,j in Tasks)
        ct61:
        b[i][j] == sum(k in Procs)bp[k][i][j];


    /*whether two tasks have communication cost*/
    forall(i,j in Tasks: i!=j)
      ct7:
        {
        o[i][j] >= Dep[i][j] - b[i][j] ;
        o[i][j] <= Dep[i][j];
        (b[i][j]==0)+(Dep[i][j]==0)+ (o[i][j]==0)>=1;
        }

    /* relation between tile and core */
    forall(k in Procs)
        sum(c in Procs)c2t[k][c]<=1;
    forall(c in Procs)
        sum(k in Procs)c2t[k][c]==1;

/* relation between task and core */
    forall(i in Tasks, c,k in Procs){
        (Map[i][k]==0)+(c2t[k][c]==0)+(a2c[i][c]==1)>=1;
    }
     forall(i in Tasks)
        sum(c in Procs)a2c[i][c]==1;
    /*the execution sequence on every processor*/
    forall(i,j in Tasks, k,l in Procs: k!=l){
        ct80:
            q[k][i][i] == 0;
            (q[k][i][j]==1) + (q[l][i][j]==1) <=1;
    }
    forall(i,j in Tasks,k in Procs:i!=j){
        ct81:
            (sum(i,j in Tasks)(bp[k][i][j]))/2==sum(i,j in Tasks)(q[k][i][j]);
            q[k][i][j]+q[k][j][i]>=bp[k][i][j];
    }
    forall(i,j,l in Tasks,k in Procs:i!=j && j!=l){
        ct82:
            (q[k][i][j] + q[k][j][l] == 2) <= q[k][i][l];
    }

    /* the distance between i and j*/
    forall(i,j in Tasks, u in Cycle: i!=j)

        ct10:
        {
        dis[i][j]>=0;
        dis[i][j]<=xN+yN-2;
        dis[i][j]>=sum(k1,k2 in Procs)(Map[i][k1] + Map[j][k2] == 2) * (abs(xP[k1]-xP[k2])+abs(yP[k1]-yP[k2]));
        dis[i][j]<=sum(k1,k2 in Procs)(Map[i][k1] + Map[j][k2] == 2) * (abs(xP[k1]-xP[k2])+abs(yP[k1]-yP[k2]));
    }

/*=====================================================================*/
    ////////////////////////

    /*the execution time*/
    forall(i in Tasks, u in Cycle)
        eq0:
        fin[u][i] - tao[u][i] >= sum(c in Procs)(Time[c][i]*a2c[i][c]);

    forall(i,j in Tasks, u in Cycle)
        eq1:
        if (Dep[i][j]==1){
            fin[u][i] <= se[u][i][j] ;
            fe[u][i][j]<= tao[u][j];}

    /*the cost spent for tranmission*/
    forall(i,j in Tasks, u in Cycle)
        eq3:
        {
            if (comm[i][j]==0){
                se[u][i][j]==0;
                fe[u][i][j]==0;
            }
            else{
                se[u][i][j]<=fe[u][i][j];
                (o[i][j]==0) + (se[u][i][j] + comm[i][j]*dis[i][j]*link+(dis[i][j]+1)*rout-fe[u][i][j]<=0)>=1;
                (o[i][j]==1) + (se[u][i][j] -fe[u][i][j]==0)>=1;
                }
        }


    /*the total cost is larger than the last execution of the last task*/
    forall(i in Tasks)
      s1:
        MP >=tao[Cycles][i] + sum(k in Procs)(Time[k][i]*a2c[i][k]);

 ////////////////////////////////////////////////////////////
/*=====================================================================*/

    /*the execution sequence in the same processor*/
    
    forall(i,j in Tasks, u in Cycle, k in Procs: i!=j)
        s3:
            fin[u][i] <= tao[u][j] + Max* (1-q[k][i][j]) ;

    /*the same task on different cycles*/
    
    forall(i in Tasks,u,v in Cycle){
        s4:
        if(u<v)
        fin[u][i] <= tao[v][i];
    }

    /*the execution of a task in later cycles should be later than the last executed task in earlier cycles*/
    
    forall(i,j in Tasks,u,v in Cycle,k in Procs){
      s5:
        if(u<v)
            fin[u][j] <= tao[v][i] + Max*(1-q[k][i][j]);
    }


    /*two tasks on the same processor cannot overlap*/
    forall(i,j in Tasks,u,v in Cycle){
        s6:
        (b[i][j]==0) + (tao[u][j]- fin[v][i]>= 0) + (tao[v][i]-fin[u][j]>=0 ) >=1;
    }

    /*two transfer from the same source and occupying the same link should be sequentical*/
    forall(i,j,l in Tasks,u in Cycle: j!=l)
        s7:
        (conflict[i][j][i][l]==0)+(abs(se[u][i][j]-se[u][i][l])-delay>=0)>=1;


    /*two data transfer on the same resource cannot overlap*/
    forall(i,j,l,r in Tasks, u,v in Cycle:i!=l ||j!=r){
    s8:

        (conflict[i][j][l][r]==0)+(abs(se[u][i][j]-se[u][l][r])>=delay) + (se[u][i][j]- fe[v][l][r]>= 0) + (se[v][l][r]-fe[u][i][j]>=0 ) >=1;

    }

}
