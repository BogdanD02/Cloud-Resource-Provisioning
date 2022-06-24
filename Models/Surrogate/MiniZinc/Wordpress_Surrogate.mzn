
include "Modules/Constraints.mzn";

int : WPInstances;
var 0..1024 : Wordpress;
var 0..1024 : MySQL;
var 0..1024 : DNS_LoadBalancer;
var 0..1024 : HTTP_LoadBalancer;
var 0..1024 : Varnish;

%
% Use case constraints
%
constraint basicAllocation({Wordpress, MySQL, Varnish});

% In order to correctly estimate the number of VM required
% we disregard the exclusive deployment component and compute
% the number of VMs required for each component in that relation.
% Afterwards we take the highest number of them into the equation.
constraint if DNS_LoadBalancer > 0 then
  provide(Wordpress, DNS_LoadBalancer, 7)
endif;

constraint if HTTP_LoadBalancer > 0 then
  provide(Wordpress, HTTP_LoadBalancer, 3)
endif;

constraint HTTP_LoadBalancer + DNS_LoadBalancer >= 1;
constraint requireProvide(Wordpress, MySQL, 2, 3);
constraint lowerBound(Varnish,2);
constraint lowerBound(MySQL, 2);
constraint upperBound(DNS_LoadBalancer, 1);
constraint lowerBound(Wordpress, WPInstances);

solve minimize Wordpress + MySQL + DNS_LoadBalancer + HTTP_LoadBalancer + Varnish;
