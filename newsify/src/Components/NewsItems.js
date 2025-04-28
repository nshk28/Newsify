import React, { Component } from 'react'

export class NewsItems extends Component {
    constructor(){
        super();
        this.state = {
            
        }
    }
  render() {
    let {title,description, imgUrl, newsUrl} = this.props;
    return (
      <div>
        {/* This is newsItem component. */}
        <div className="card" style={{width: "18rem"}}>
            <img src={imgUrl} className="card-img-top" alt="..."/>
                <div className="card-body">
                    <h5 className="card-title">{title}...</h5>
                    <p className="card-text">{description}...</p>
                    <a href={newsUrl} target ="_ blank" className="btn btn-sm btn-dark">Read More</a>
                </div>
            </div>
      </div>
    )
  }
}

export default NewsItems
