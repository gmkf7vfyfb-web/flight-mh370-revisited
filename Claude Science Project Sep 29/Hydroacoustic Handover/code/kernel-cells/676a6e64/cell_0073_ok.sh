G=/Users/pete/Downloads/mh370-exchange/hydroacoustics
du -sh $G/run-j-gated $G/run-j-gated.staging $G/run-j-imos-ram-grid $G/run-j-injection $G/run-j-levels $G/run-j-searches $G/run-j-windows $G/run-j-tl-grid $G/kadri-package-v2 $G/run-j-digitisation $G/run-j-weak-signal $G/run-j-tlrecal 2>/dev/null
W=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces; du -sh $W/c1f32191* $W/ab0373ea* $W/e048f943* 2>/dev/null
du -sh /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts 2>/dev/null
ls $G/run-j-gated.staging 2>/dev/null | head -5; ls $G/run-j-gated 2>/dev/null | head -5; cat $G/run-j-gated/READY 2>/dev/null | head -2