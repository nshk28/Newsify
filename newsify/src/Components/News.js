import React, { Component } from "react";
import NewsItems from "./NewsItems";

export class News extends Component {
  constructor() {
    super();
    this.state = {
      articles: [],
      loading: false,
      page: 1
    };
  }
  async componentDidMount() {
    let url =
      "https://newsapi.org/v2/top-headlines?country=in&apiKey=7463a5fe791c4b8c8b2c33161dfa9009&page=1&pageSize=20";
    let data = await fetch(url);
    let parsedData = await data.json();
    console.log(parsedData);
    this.setState({ articles: parsedData.articles , totalResults : parsedData.totalResults});
  }

  handlePrevClick = async () => {
    let url =
      `https://newsapi.org/v2/top-headlines?country=in&apiKey=7463a5fe791c4b8c8b2c33161dfa9009&page=${this.state.page -1}&pageSize=20`;
    let data = await fetch(url);
    let parsedData = await data.json();
     console.log(parsedData);
    this.setState({
      page: this.state.page - 1,
      articles: parsedData.articles 
    });
  };

  handleNextClick = async () => {
    if (this.state.page+1 > Math.ceil(this.state.totalResults/20)){
      return;

    }else{
      let url =
      `https://newsapi.org/v2/top-headlines?country=in&apiKey=7463a5fe791c4b8c8b2c33161dfa9009&page=${this.state.page+1}&pageSize=20`;
    let data = await fetch(url);
    let parsedData = await data.json();
     console.log(parsedData);
    this.setState({
      page: this.state.page + 1,
      articles: parsedData.articles 
    });

    }
    
  };
  render() {
    return (
      <div className="container my-3">
        <h1 className="text-center"> Newsify: Top Headlines</h1>
       
        <div className="row my-3">
          {this.state.articles.map((element) => {
            return (
              <div className="col-md-4 my-3" key={element.url}>
                <NewsItems
                  title={element.title}
                  description={element.description}
                  imgUrl={element.urlToImage}
                  newsUrl={element.url}
                />
              </div>
            );
          })}
        </div>
        <div className="container d-flex justify-content-between">
          <button
            disabled={this.state.page <= 1}
            type="button"
            className="btn btn-primary"
            onClick={this.handlePrevClick}
          >
            &larr; Previous
          </button>
          <button
            disabled={this.state.page+1 > Math.ceil(this.state.totalResults/20)}
            type="button"
            className="btn btn-primary"
            onClick={this.handleNextClick}
          >
            Next &rarr;
          </button>
        </div>
      </div>
    );
  }
}

export default News;
