import React, { Component } from 'react';
import { Switch, Route } from 'react-router-dom'


class Main extends Component {
  
  constructor(props) {
    super(props);
  }
  
  render() {
    return (
        <Switch>
          <Route exact path="/" component={Login} />
          <Route path="/callback" component={LoginCallback} />
        </Switch>
    );
  }
}

export default Main;