
int : WPInstances;
var 0..1024 : Wordpress;
var 0..1024 : MySQL;
var 0..1024 : DNS_LoadBalancer;
var 0..1024 : HTTP_LoadBalancer;
var 0..1024 : Varnish;

predicate requireProvide( var int: alphaCompId, var int: betaCompId, int: alphaCompIdInstances, int: betaCompIdInstances ) 
          = alphaCompId * alphaCompIdInstances <= betaCompId * betaCompIdInstances ;
          
predicate Provide(var int: alphaCompId, var int: betaCompId, int: alphaCompIdInstances)
          = alphaCompId <= alphaCompIdInstances * betaCompId;

predicate lowerBound (var int: compId, int: bound) =  compId >= bound;

predicate upperBound (var int: compId, int: bound) =  compId <= bound;

predicate exclusiveDeployment( var int: alphaCompId, var int: betaCompId)
          = (alphaCompId > 0 /\ betaCompId = 0) \/ (alphaCompId = 0 /\ betaCompId > 0);


%
% Use case constraints
%
constraint DNS_LoadBalancer > 0 -> Provide(WPInstances, DNS_LoadBalancer, 7);
constraint HTTP_LoadBalancer > 0 -> Provide(WPInstances, HTTP_LoadBalancer, 3);

constraint requireProvide(WPInstances, MySQL, 2, 3);
constraint lowerBound(Varnish,2);
constraint lowerBound(MySQL, 2);
constraint upperBound(DNS_LoadBalancer, 1);
constraint exclusiveDeployment(DNS_LoadBalancer,HTTP_LoadBalancer);
constraint lowerBound(Wordpress, WPInstances);

solve minimize Wordpress + MySQL + DNS_LoadBalancer + HTTP_LoadBalancer + Varnish;
