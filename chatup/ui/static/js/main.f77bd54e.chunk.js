(this["webpackJsonpchatup-ui"]=this["webpackJsonpchatup-ui"]||[]).push([[0],{163:function(e,t,a){e.exports=a(192)},192:function(e,t,a){"use strict";a.r(t);var n=a(0),r=a.n(n),l=a(43),o=a.n(l),c=a(28),u=a(26),s=a(32),i=a(30),m=a(18),h=a(20),d=a(10),p=a(70),g=a(205),E=a(212),f=a(208),b=a(214),w=a(193),j=a(211),v=a(34),I=a.n(v),S="https://chatup-vezaks.herokuapp.com";var C=function(e,t,a,n,r,l){return{type:"AUTH_SUCCESS",token:e,username:t,watchtime:a,userID:n,username_color:r,roleID:l}},O=function(e){return{type:"AUTH_FAIL",error:e}},A=function(){return I.a.defaults.xsrfHeaderName="X-CSRFTOKEN",I.a.defaults.xsrfCookieName="csrftoken",I.a.get("".concat(S,"/api/auth/logout/"),{withCredentials:!0,headers:{"Content-Type":"application/json"}}).then((function(){localStorage.clear()})),{type:"AUTH_LOGOUT"}},y=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(){var e;Object(c.a)(this,a);for(var n=arguments.length,r=new Array(n),l=0;l<n;l++)r[l]=arguments[l];return(e=t.call.apply(t,[this].concat(r))).state={username:"",password:""},e.handleChange=function(t){e.setState(Object(p.a)({},t.target.name,t.target.value))},e.handleSubmit=function(t){t.preventDefault();var a=e.state,n=a.username,r=a.password;e.props.login(n,r)},e}return Object(u.a)(a,[{key:"render",value:function(){var e=this.props,t=e.error,a=e.loading,n=e.token,l=this.state,o=l.username,c=l.password;return n?r.a.createElement(d.a,{to:"/"}):r.a.createElement(g.a,{textAlign:"center",style:{height:"100vh"},verticalAlign:"middle"},r.a.createElement(g.a.Column,{style:{maxWidth:450}},r.a.createElement(E.a,{as:"h2",color:"teal",textAlign:"center"},"Log-in to your account"),t&&r.a.createElement("p",null,this.props.error.message),r.a.createElement(r.a.Fragment,null,r.a.createElement(f.a,{size:"large",onSubmit:this.handleSubmit},r.a.createElement(b.a,{stacked:!0},r.a.createElement(f.a.Input,{onChange:this.handleChange,value:o,name:"username",fluid:!0,icon:"user",iconPosition:"left",placeholder:"Username"}),r.a.createElement(f.a.Input,{onChange:this.handleChange,fluid:!0,value:c,name:"password",icon:"lock",iconPosition:"left",placeholder:"Password",type:"password"}),r.a.createElement(w.a,{color:"teal",fluid:!0,size:"large",loading:a,disabled:a},"Login"))),r.a.createElement(j.a,null,"New to us? ",r.a.createElement(m.c,{to:"/signup"},"Sign Up")))))}}]),a}(r.a.Component),D=Object(h.b)((function(e){return{loading:e.auth.loading,error:e.auth.error,token:e.auth.token}}),(function(e){return{login:function(t,a){return e(function(e,t){return function(a){a({type:"AUTH_START"}),I.a.defaults.xsrfHeaderName="X-CSRFTOKEN",I.a.defaults.xsrfCookieName="csrftoken",I.a.post("".concat(S,"/api/auth/login/"),{username:e,password:t},{credentials:"include",withCredentials:!0}).then((function(){I.a.get("".concat(S,"/api/general/user/"),{withCredentials:!0,headers:{"Content-Type":"application/json"}}).then((function(e){localStorage.setItem("token","true"),localStorage.setItem("username",e.data.username),localStorage.setItem("watchtime",e.data.watchtime),localStorage.setItem("userID",e.data.id),localStorage.setItem("username_color",e.data.username_color),localStorage.setItem("roleID",e.data.role);var t=e.data.username,n=e.data.watchtime,r=e.data.id,l=e.data.username_color,o=e.data.role;a(C("true",t,n,r,l,o))}))})).catch((function(e){a(O(e))}))}}(t,a))}}}))(y),k=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(){var e;Object(c.a)(this,a);for(var n=arguments.length,r=new Array(n),l=0;l<n;l++)r[l]=arguments[l];return(e=t.call.apply(t,[this].concat(r))).state={username:"",email:"",password1:"",password2:""},e.handleSubmit=function(t){t.preventDefault();var a=e.state,n=a.username,r=a.email,l=a.password1,o=a.password2;e.props.signup(n,r,l,o)},e.handleChange=function(t){e.setState(Object(p.a)({},t.target.name,t.target.value))},e}return Object(u.a)(a,[{key:"render",value:function(){var e=this.state,t=e.username,a=e.email,n=e.password1,l=e.password2,o=this.props,c=o.error,u=o.loading;return o.token?r.a.createElement(d.a,{to:"/"}):r.a.createElement(g.a,{textAlign:"center",style:{height:"100vh"},verticalAlign:"middle"},r.a.createElement(g.a.Column,{style:{maxWidth:450}},r.a.createElement(E.a,{as:"h2",color:"teal",textAlign:"center"},"Signup to your account"),c&&r.a.createElement("p",null,this.props.error.message),r.a.createElement(r.a.Fragment,null,r.a.createElement(f.a,{size:"large",onSubmit:this.handleSubmit},r.a.createElement(b.a,{stacked:!0},r.a.createElement(f.a.Input,{onChange:this.handleChange,value:t,name:"username",fluid:!0,icon:"user",iconPosition:"left",placeholder:"Username"}),r.a.createElement(f.a.Input,{onChange:this.handleChange,value:a,name:"email",fluid:!0,icon:"mail",iconPosition:"left",placeholder:"E-mail address"}),r.a.createElement(f.a.Input,{onChange:this.handleChange,fluid:!0,value:n,name:"password1",icon:"lock",iconPosition:"left",placeholder:"Password",type:"password"}),r.a.createElement(f.a.Input,{onChange:this.handleChange,fluid:!0,value:l,name:"password2",icon:"lock",iconPosition:"left",placeholder:"Confirm password",type:"password"}),r.a.createElement(w.a,{color:"teal",fluid:!0,size:"large",loading:u,disabled:u},"Signup"))),r.a.createElement(j.a,null,"Already have an account? ",r.a.createElement(m.c,{to:"/login"},"Login")))))}}]),a}(r.a.Component),H=Object(h.b)((function(e){return{loading:e.auth.loading,error:e.auth.error,token:e.auth.token}}),(function(e){return{signup:function(t,a,n,r){return e(function(e,t,a,n){return function(r){r({type:"AUTH_START"}),I.a.defaults.xsrfHeaderName="X-CSRFTOKEN",I.a.defaults.xsrfCookieName="csrftoken",I.a.post("".concat(S,"/api/auth/signup/"),{username:e,email:t,password1:a,password2:n},{credentials:"include",withCredentials:!0}).then((function(){I.a.get("".concat(S,"/api/general/user/"),{withCredentials:!0,headers:{"Content-Type":"application/json"}}).then((function(e){localStorage.setItem("token","true"),localStorage.setItem("username",e.data.username),localStorage.setItem("watchtime",e.data.watchtime),localStorage.setItem("userID",e.data.id),localStorage.setItem("username_color",e.data.username_color),localStorage.setItem("roleID",e.data.role);var t=e.data.username,a=e.data.watchtime,n=e.data.id,l=e.data.username_color,o=e.data.role;r(C("true",t,a,n,l,o))}))})).catch((function(e){r(O(e))}))}}(t,a,n,r))}}}))(k),R=a(146),x=a(145),P=a(148),q=a.n(P),T=function(e){return e.children},M=a(210),U=a(150),V=a(206),B=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).state={message:""},n.messageChangeHandler=function(e){n.setState({message:e.target.value})},n.sendMessageHandler=function(e){e.preventDefault(),n.setState({message:""})},n.renderMessages=function(e){},n.scrollToBottom=function(){n.messagesEnd.scrollIntoView({behavior:"smooth"})},n.initialiseChat(),n}return Object(u.a)(a,[{key:"initialiseChat",value:function(){}}]),Object(u.a)(a,[{key:"componentDidMount",value:function(){this.scrollToBottom()}},{key:"componentDidUpdate",value:function(){this.scrollToBottom()}},{key:"render",value:function(){var e=this;return r.a.createElement(T,null,r.a.createElement("div",{className:"messages"},r.a.createElement(M.a,{relaxed:!0},r.a.createElement(M.a.Item,null,r.a.createElement(U.a,{avatar:!0,src:"data:image/png;base64,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"}),r.a.createElement(M.a.Content,null,r.a.createElement(M.a.Header,{as:"a"},this.props.username?this.props.username:"Unknown"),r.a.createElement(M.a.Description,null,"\u041a\u0430\u043a \u0432\u0430\u043c"," ",r.a.createElement("a",{href:"https://react.semantic-ui.com/"},r.a.createElement("b",null,"Semantic UI React")),"? \u0412\u0440\u043e\u0434\u0435 \u043d\u0438\u0447\u0435\u0433\u043e."))),r.a.createElement(M.a.Item,null,r.a.createElement(U.a,{avatar:!0,src:"https://static-cdn.jtvnw.net/badges/v1/b817aba4-fad8-49e2-b88a-7cc744dfa6ec/3"}),r.a.createElement(M.a.Content,null,r.a.createElement(M.a.Header,{as:"a"},"marstvi"),r.a.createElement(M.a.Description,null,"\u041c\u043d\u0435 \u0431\u043e\u043b\u044c\u0448\u0435 \u043d\u0440\u0430\u0432\u0438\u0442\u0441\u044f "," ",r.a.createElement("a",{href:"https://material-ui.com/ru//"},r.a.createElement("b",null,"Material-UI"))," \u0438\u043b\u0438 \u0442\u043e\u0442 \u0436\u0435"," ",r.a.createElement("a",{href:"https://github.com/react-bootstrap/react-bootstrap"},r.a.createElement("b",null,"Bootstrap")),"."))),r.a.createElement(M.a.Item,null,r.a.createElement(U.a,{avatar:!0,src:"https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTyxlcQ5PY2EARmYr40DfRwP7xwV-qhy3yMuA&usqp=CAU"}),r.a.createElement(M.a.Content,null,r.a.createElement(M.a.Header,{as:"a"},"Max_of_Shadows"),r.a.createElement(M.a.Description,null,"\u041d\u0435\u043f\u043b\u043e\u0445\u043e \u0431\u044b \u043f\u043e\u0443\u0447\u0438\u0442\u044c"," ",r.a.createElement("a",{href:"https://reactjs.org/"},r.a.createElement("b",null,"React")),", ","\u043f\u043e\u043f\u0443\u043b\u044f\u0440\u043d\u044b\u0439 \u0444\u0440\u0435\u0439\u043c\u0432\u043e\u0440\u043a."))),r.a.createElement(M.a.Item,null,r.a.createElement(U.a,{avatar:!0,src:"https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/3"}),r.a.createElement(U.a,{avatar:!0,src:"https://static-cdn.jtvnw.net/badges/v1/f9cc2879-ab6f-4c6a-94b9-5a414822b0dd/3"}),r.a.createElement(M.a.Content,null,r.a.createElement(M.a.Header,{as:"a"},"Vezaks"),r.a.createElement(M.a.Description,null,"\u042d\u043b\u0438\u0442\u043d\u043e\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u0441\u0442\u0432\u043e.")))),r.a.createElement("div",{style:{float:"left",clear:"both"},ref:function(t){e.messagesEnd=t}})),r.a.createElement("div",{className:"message-input"},r.a.createElement("form",{onSubmit:this.sendMessageHandler},r.a.createElement("div",{className:"wrap"},r.a.createElement(V.a,{onChange:this.messageChangeHandler,value:this.state.message,required:!0,id:"chat-message-input",type:"text",placeholder:"Write your message...",fluid:!0})))))}}]),a}(r.a.Component),z=Object(h.b)((function(e){return{username:e.auth.username}}))(B),F=function(){return r.a.createElement("div",null,r.a.createElement("br",null),r.a.createElement("br",null),r.a.createElement(g.a,{divided:!0,celled:!0},r.a.createElement(R.a,null,r.a.createElement(x.a,{width:12},r.a.createElement(b.a,{compact:!1},r.a.createElement(q.a,{poster:"https://sun9-35.userapi.com/c849532/v849532312/15082b/efNn97HREgo.jpg",url:"//d2zihajmogu5jn.cloudfront.net/bipbop-advanced/bipbop_16x9_variant.m3u8",autoplay:!1,controls:!0,width:1370,height:800}))),r.a.createElement(x.a,{width:4},r.a.createElement(b.a,null,r.a.createElement(z,null))))))},G={3:"\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440",2:"\u041c\u043e\u0434\u0435\u0440\u0430\u0442\u043e\u0440",4:"\u0421\u0442\u0440\u0438\u043c\u0435\u0440",1:"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c"},L=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(u.a)(a,[{key:"render",value:function(){return void 0===this.props.token?r.a.createElement(d.a,{to:"/"}):r.a.createElement("div",{className:"contact-profile"},r.a.createElement("br",null),r.a.createElement("br",null),r.a.createElement("br",null),null!==this.props.username?r.a.createElement(T,null,r.a.createElement("img",{src:"https://static-cdn.jtvnw.net/jtv_user_pictures/f978fcd7-c028-4d02-8b64-bf9f468ecad3-profile_image-300x300.png",alt:""}),r.a.createElement("p",null,"User ID: ",this.props.userID),r.a.createElement("p",null,"Username: ",this.props.username),r.a.createElement("p",null,"Role: ",G[this.props.roleID]),r.a.createElement("p",null,"Watchtime: ",this.props.watchtime),r.a.createElement("p",null,"Username color: ",this.props.username_color)):null)}}]),a}(r.a.Component),N=Object(h.b)((function(e){return{username:e.auth.username,watchtime:e.auth.watchtime,username_color:e.auth.username_color,userID:e.auth.userID,roleID:e.auth.roleID,token:e.auth.token}}))(L),Z=function(){return r.a.createElement(T,null,r.a.createElement(d.b,{path:"/login",component:D}),r.a.createElement(d.b,{path:"/signup",component:H}),r.a.createElement(d.b,{exact:!0,path:"/",component:F}),r.a.createElement(d.b,{exact:!0,path:"/swagger/",render:function(){return window.location="".concat(S,"/api/docs/")}}),r.a.createElement(d.b,{exact:!0,path:"/profile/",component:N}))},X=(a(191),a(209)),K=a(207),Y={3:"\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440",2:"\u041c\u043e\u0434\u0435\u0440\u0430\u0442\u043e\u0440",4:"\u0421\u0442\u0440\u0438\u043c\u0435\u0440",1:"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c"},J=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(u.a)(a,[{key:"render",value:function(){var e=this,t=this.props,a=t.authenticated,n=t.username,l=t.roleID;return r.a.createElement("div",null,r.a.createElement(X.a,{fixed:"top",inverted:!0,size:"large"},r.a.createElement(K.a,null,a?r.a.createElement(r.a.Fragment,null,r.a.createElement(m.b,{to:"/"},r.a.createElement(X.a.Item,{header:!0},"Home")),r.a.createElement(m.b,{to:"/profile/"},r.a.createElement(X.a.Item,{header:!0},"Profile"))):r.a.createElement(m.b,{to:"/"},r.a.createElement(X.a.Item,{header:!0},"Home")),r.a.createElement(r.a.Fragment,null,r.a.createElement(m.b,{to:"/swagger/"},r.a.createElement(X.a.Item,{header:!0},"API")))),a?r.a.createElement(r.a.Fragment,null,r.a.createElement(X.a.Menu,{position:"right"},r.a.createElement(X.a.Item,null,n),r.a.createElement(X.a.Item,null,Y[l]),r.a.createElement(X.a.Item,{header:!0,onClick:function(){return e.props.logout()}},"Logout"))):r.a.createElement(r.a.Fragment,null,r.a.createElement(m.b,{to:"/login"},r.a.createElement(X.a.Item,{header:!0},"Login")),r.a.createElement(m.b,{to:"/signup"},r.a.createElement(X.a.Item,{header:!0},"Signup")))),this.props.children,r.a.createElement(b.a,{inverted:!0,vertical:!0,style:{margin:"0em 0em 0em",padding:"2.8em 0em"}}))}}]),a}(r.a.Component),Q=Object(d.f)(Object(h.b)((function(e){return{authenticated:null!==e.auth.token,username:e.auth.username,roleID:e.auth.roleID}}),(function(e){return{logout:function(){return e(A())}}}))(J)),W=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(u.a)(a,[{key:"componentDidMount",value:function(){this.props.isAuthenticated||this.props.onTryAutoSignup()}},{key:"render",value:function(){return r.a.createElement(m.a,null,r.a.createElement(Q,this.props,r.a.createElement(Z,null)))}}]),a}(n.Component),_=Object(h.b)((function(e){return{isAuthenticated:null!==e.auth.token}}),(function(e){return{onTryAutoSignup:function(){return e((function(e){var t=localStorage.getItem("token"),a=localStorage.getItem("username"),n=localStorage.getItem("watchtime"),r=localStorage.getItem("userID"),l=localStorage.getItem("username_color"),o=localStorage.getItem("roleID");e(void 0===t?A():C(t,a,n,r,l,o))}))},setProfile:function(t,a,n){return e(function(e,t,a){return{type:"AUTH_UPDATE",username:e,watchtime:t,username_color:a}}(t,a,n))}}}))(W);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));var $=a(64),ee=a(149),te=a(129),ae=function(e,t){return Object(te.a)(Object(te.a)({},e),t)},ne={token:null,error:null,loading:!1,username:null,watchtime:null,userID:null,username_color:null,roleID:null},re=function(e,t){return ae(e,{error:null,loading:!0})},le=function(e,t){return ae(e,{token:t.token,error:null,loading:!1,username:t.username,watchtime:t.watchtime,userID:t.userID,username_color:t.username_color,roleID:t.roleID})},oe=function(e,t){return ae(e,{error:t.error,loading:!1})},ce=function(e,t){return ae(e,{token:null,username:null,watchtime:null,userID:null,username_color:null,roleID:null})},ue=function(e,t){return ae(e,{username:t.username,watchtime:t.watchtime,username_color:t.username_color})},se=function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:ne,t=arguments.length>1?arguments[1]:void 0;switch(t.type){case"AUTH_START":return re(e);case"AUTH_SUCCESS":return le(e,t);case"AUTH_FAIL":return oe(e,t);case"AUTH_LOGOUT":return ce(e);case"AUTH_UPDATE":return ue(e,t);default:return e}},ie=window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__||$.d,me=Object($.c)({auth:se}),he=Object($.e)(me,ie(Object($.a)(ee.a))),de=r.a.createElement(h.a,{store:he},r.a.createElement(_,null));o.a.render(de,document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[163,1,2]]]);
//# sourceMappingURL=main.f77bd54e.chunk.js.map