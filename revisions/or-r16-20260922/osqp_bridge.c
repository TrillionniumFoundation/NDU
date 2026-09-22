/* A minimal checked bridge to the OSQP library bundled with CasADi 3.7.2.
   All repeated solves update q only: the factorization is genuinely cached. */
#include <stdlib.h>
#include <string.h>
#include <osqp.h>
void *ndu_setup(long long n,long long m,long long pn,long long *pp,long long *pi,double *px,
                long long an,long long *ap,long long *ai,double *ax,double *q,double *l,double *u,double eps) {
  csc P={pn,n,n,pp,pi,px,-1}, A={an,m,n,ap,ai,ax,-1};
  OSQPData data={n,m,&P,&A,q,l,u}; OSQPSettings settings;
  osqp_set_default_settings(&settings); settings.verbose=0; settings.polish=1;
  settings.eps_abs=eps; settings.eps_rel=eps; settings.max_iter=500000;
  settings.warm_start=1; settings.adaptive_rho_interval=25;
  OSQPWorkspace *w=NULL;
  if(osqp_setup(&w,&data,&settings)!=0) return NULL;
  return w;
}
int ndu_solve(void *ptr,double *q,double *x0,double *y0,int cold,
              double *x,double *y,long long *iters) {
  OSQPWorkspace *w=(OSQPWorkspace*)ptr;
  if(!w || osqp_update_lin_cost(w,q)) return -100;
  if(cold) { osqp_warm_start(w,x0,y0); }
  if(osqp_solve(w)) return -101;
  memcpy(x,w->solution->x,w->data->n*sizeof(double));
  memcpy(y,w->solution->y,w->data->m*sizeof(double)); *iters=w->info->iter;
  return (int)w->info->status_val;
}
void ndu_close(void *ptr){if(ptr)osqp_cleanup((OSQPWorkspace*)ptr);}
